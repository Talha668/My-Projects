from django.core.management.base import BaseCommand
from django.utils import timezone
from restaurant.models import SalesReport, Order
from django.db.models import Sum, Count

class Command(BaseCommand):
    help = 'Generate daily sales report'
    
    def handle(self, *args, **options):
        yesterday = timezone.now().date() - timezone.timedelta(days=1)
        
        orders = Order.objects.filter(
            created_at__date=yesterday,
            status='paid'
        )
        
        total_orders = orders.count()
        total_revenue = orders.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
        total_customers = orders.values('customer_name').distinct().count()
        avg_order_value = total_revenue / total_orders if total_orders > 0 else 0
        
        SalesReport.objects.update_or_create(
            report_date=yesterday,
            defaults={
                'total_orders': total_orders,
                'total_revenue': total_revenue,
                'total_customers': total_customers,
                'average_order_value': avg_order_value
            }
        )
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully generated report for {yesterday}')
        )