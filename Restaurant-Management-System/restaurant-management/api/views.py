from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import datetime, timedelta
from restaurant.models import *
from api.serializers import *
from django.shortcuts import get_object_or_404


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class MenuItemViewSet(viewsets.ModelViewSet):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    
    @action(detail=False, methods=['get'])
    def available(self, request):
        available_items = MenuItem.objects.filter(is_available=True)
        serializer = self.get_serializer(available_items, many=True)
        return Response(serializer.data)


class TableViewSet(viewsets.ModelViewSet):
    queryset = Table.objects.all()
    serializer_class = TableSerializer
    
    @action(detail=False, methods=['get'])
    def available(self, request):
        date = request.query_params.get('date')
        time = request.query_params.get('time')
        party_size = request.query_params.get('party_size')
        
        if not all([date, time, party_size]):
            return Response({'error': 'Date, time and party_size parameters are required'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        try:
            party_size = int(party_size)
            reservation_datetime = datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")
        except ValueError:
            return Response({'error': 'Invalid date/time format'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        # Find tables that are available and can accommodate the party
        available_tables = Table.objects.filter(
            capacity__gte=party_size,
            status='available'
        ).exclude(
            reservation__reservation_date=date,
            reservation__reservation_time=time,
            reservation__status__in=['confirmed', 'pending']
        )
        
        serializer = self.get_serializer(available_tables, many=True)
        return Response(serializer.data)


class ReservationViewSet(viewsets.ModelViewSet):
    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer
    
    def create(self, request, *args, **kwargs):
        # Check table availability before creating reservation
        table_id = request.data.get('table')
        reservation_date = request.data.get('reservation_date')
        reservation_time = request.data.get('reservation_time')
        
        if table_id and reservation_date and reservation_time:
            conflicting_reservation = Reservation.objects.filter(
                table_id=table_id,
                reservation_date=reservation_date,
                reservation_time=reservation_time,
                status__in=['confirmed', 'pending']
            ).exists()
            
            if conflicting_reservation:
                return Response(
                    {'error': 'Table is already reserved for this date and time'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        return super().create(request, *args, **kwargs)


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    
    def create(self, request, *args, **kwargs):
        # Create order with items and update inventory
        order_data = request.data
        items_data = order_data.pop('items', [])
        
        serializer = self.get_serializer(data=order_data)
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        
        # Create order items
        total_amount = 0
        for item_data in items_data:
            menu_item = MenuItem.objects.get(id=item_data['menu_item'])
            order_item = OrderItem.objects.create(
                order=order,
                menu_item=menu_item,
                quantity=item_data['quantity'],
                unit_price=menu_item.price,
                notes=item_data.get('notes', '')
            )
            total_amount += order_item.total_price
            
            # Update inventory (simplified - in real app, you'd have recipe ingredients)
            # self.update_inventory(menu_item, item_data['quantity'])
        
        order.total_amount = total_amount
        order.save()
        
        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        order = self.get_object()
        new_status = request.data.get('status')
        
        if new_status not in dict(Order.ORDER_STATUS):
            return Response({'error': 'Invalid status'}, status=status.HTTP_400_BAD_REQUEST)
        
        order.status = new_status
        order.save()
        
        return Response({'status': 'Status updated successfully'})
    
    @action(detail=False, methods=['get'])
    def today_orders(self, request):
        today = timezone.now().date()
        orders = Order.objects.filter(created_at__date=today)
        serializer = self.get_serializer(orders, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def prcess_payment(self, request, pk=None):
        order = self.get_object()
        payment_amount = request.data.get('amount')

        if not payment_amount:
            return Response({'error': 'Payment amount required'}, status=status.HTTP_400_BAD_REQUEST)
        
        if float(payment_amount) >= float(order.total_amount):
            order.status = 'paid'
            order.save()

            # Update table status
            order.table.status = 'available'
            order.table.save()

            return Response({'status': 'Payment successful', 'order_status': 'paid'})
        else:
            return Response({'error': 'Insufficient payment'}, status=status.HTTP_400_BAD_REQUEST)
        

class InventoryViewSet(viewsets.ModelViewSet):
    queryset = Inventory.objects.all()
    serializer_class = InventorySerializer
    
    @action(detail=False, methods=['get'])
    def low_stock(self, request):
        low_stock_items = Inventory.objects.filter(current_stock__lte=models.F('minimum_stock'))
        serializer = self.get_serializer(low_stock_items, many=True)
        return Response(serializer.data)


class SalesReportViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = SalesReport.objects.all()
    serializer_class = SalesReportSerializer
    
    @action(detail=False, methods=['get'])
    def generate_daily_report(self, request):
        date = request.query_params.get('date', timezone.now().date())
        
        # Calculate daily sales data
        orders = Order.objects.filter(
            created_at__date=date,
            status='paid'
        )
        
        total_orders = orders.count()
        total_revenue = orders.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
        total_customers = orders.values('customer_name').distinct().count()
        avg_order_value = total_revenue / total_orders if total_orders > 0 else 0
        
        # Create or update sales report
        report, created = SalesReport.objects.update_or_create(
            report_date=date,
            defaults={
                'total_orders': total_orders,
                'total_revenue': total_revenue,
                'total_customers': total_customers,
                'average_order_value': avg_order_value
            }
        )
        
        serializer = self.get_serializer(report)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def sales_analytics(self, request):
        """Get sales analytics for dashboard"""
        today = timezone.now().date()
        week_ago = today - timedelta(days=7)
        month_ago = today - timedelta(days=30)

        # Today stats
        today_orders = Order.objects.filter(created_at__date=today, status='paid')
        today_revenue = today_orders.aggregate(Sum('total_amount'))['total_amoungt__sum'] or 0

        # Week stats
        week_orders = Order.objects,filter(created_at__date__gte=week_ago, status='paid')
        week_revenue = week_orders.aggregate(Sum('total_amount'))['total_amount__sum'] or 0

        # Month stats
        month_orders = Order.objects.filter(created_at__date__gte=month_ago, status='paid')
        month_revenue = month_orders.aggregate(Sum('total_amount'))['total_amount__sum'] or 0

        # Popular items
        popular_items = OrderItem.objects.filter(order__created_at__date__gte=week_ago).values('menu_item__name').annotate(total_quantity=Sum('quantity')).order_by('-total_quantity')[:5]

        analytics = {
            'today': {
                'revenue': float(today_revenue),
                'orders': today_orders.count()
            },
            'week': {
                'revenue': float(week_revenue),
                'orders': week_orders.count()
            },
            'month': {
                'revenue': float(month_revenue),
                'orders': month_orders.count()
            },
            'popular_items': list(popular_items)
        }

        return Response(analytics)