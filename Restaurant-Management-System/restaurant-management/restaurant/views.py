from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import models
from django.utils import timezone
from datetime import datetime, date
from restaurant.models import Order, Table, Inventory, MenuItem, Reservation, Category, OrderItem
from .forms import InventoryForm
from .models import Inventory

@login_required
def dashboard(request):
    # Use direct database queries with model objects
    today = timezone.now().date()
    
    # Get today's orders
    orders = Order.objects.filter(created_at__date=today)
    
    # Get all tables
    tables = Table.objects.all()
    
    # Get low stock inventory
    low_stock = Inventory.objects.filter(current_stock__lte=models.F('minimum_stock'))
    
    # Calculate stats
    today_revenue = sum(order.total_amount for order in orders)
    available_tables = tables.filter(status='available').count()
    
    context = {
        'orders': orders,
        'today_revenue': today_revenue,
        'available_tables': available_tables,
        'low_stock_count': low_stock.count(),
        'recent_orders': orders.order_by('-created_at')[:5]
    }
    
    return render(request, 'restaurant/dashboard.html', context)


@login_required
def menu_management(request):
    menu_items = MenuItem.objects.all()
    categories = Category.objects.all()
    
    context = {
        'menu_items': menu_items,
        'categories': categories
    }
    return render(request, 'restaurant/menu.html', context)


@login_required
def order_management(request):
    orders = Order.objects.all().order_by('-created_at')
    tables = Table.objects.all()
    
    context = {
        'orders': orders,
        'tables': tables
    }
    return render(request, 'restaurant/orders.html', context)


@login_required
def table_management(request):
    tables = Table.objects.all()
    
    context = {
        'tables': tables
    }
    return render(request, 'restaurant/tables.html', context)


@login_required
def reservation_management(request):
    reservations = Reservation.objects.all().order_by('reservation_date', 'reservation_time')
    tables = Table.objects.all()
    
    context = {
        'reservations': reservations,
        'tables': tables
    }
    return render(request, 'restaurant/reservations.html', context)


@login_required
def inventory_management(request):
    inventory = Inventory.objects.all()
    low_stock = Inventory.objects.filter(current_stock__lte=models.F('minimum_stock'))
    
    context = {
        'inventory': inventory,
        'low_stock': low_stock
    }
    return render(request, 'restaurant/inventory.html', context)


@login_required
def create_order(request):
    if request.method == 'POST':
        try:
            table_id = request.POST.get('table')
            customer_name = request.POST.get('customer_name', '')
            notes = request.POST.get('notes', '')
            
            # Get order items data
            menu_item_ids = request.POST.getlist('menu_items')
            quantities = request.POST.getlist('quantities')
            instructions = request.POST.getlist('instructions')
            
            # Validate required fields
            if not table_id:
                messages.error(request, 'Please select a table.')
                return redirect('create_order')
            
            if not menu_item_ids or all(not item_id for item_id in menu_item_ids):
                messages.error(request, 'Please add at least one menu item to the order.')
                return redirect('create_order')
            
            table = Table.objects.get(id=table_id)
            
            # Create the order
            order = Order.objects.create(
                table=table,
                customer_name=customer_name,
                notes=notes,
                status='pending'
            )
            
            total_amount = 0
            
            # Add all order items
            for i, menu_item_id in enumerate(menu_item_ids):
                if menu_item_id and quantities[i]:
                    try:
                        menu_item = MenuItem.objects.get(id=menu_item_id)
                        quantity = int(quantities[i])
                        
                        # Create order item
                        order_item = OrderItem.objects.create(
                            order=order,
                            menu_item=menu_item,
                            quantity=quantity,
                            unit_price=menu_item.price,
                            special_instructions=instructions[i] if i < len(instructions) else ''
                        )
                        
                        total_amount += order_item.total_price
                        
                    except MenuItem.DoesNotExist:
                        messages.warning(request, f'Menu item with ID {menu_item_id} not found.')
                    except ValueError:
                        messages.warning(request, f'Invalid quantity for {menu_item.name}.')
            
            # Update order total
            order.total_amount = total_amount
            order.save()
            
            # Update table status
            table.status = 'occupied'
            table.save()
            
            messages.success(request, f'Order {order.order_number} created successfully!')

            # Redirect for the create order page to return to orders page
            return redirect('order_management') 
            

        except Table.DoesNotExist:
            messages.error(request, 'Selected table not found.')
        except Exception as e:
            messages.error(request, f'Error creating order: {str(e)}')
    
    # GET request - show form
    tables = Table.objects.filter(status='available')
    menu_items = MenuItem.objects.filter(is_available=True)
    
    context = {
        'tables': tables,
        'menu_items': menu_items
    }
    return render(request, 'restaurant/create_order.html', context)


@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    order_items = order.items.all()

    context = {
        'order': order,
        'order_items': order_items
    }
    
    return render(request, 'restaurant/order_detail.html', context)


@login_required
def update_order_status(request, order_id):
    if request.method == 'POST':
        try:
            order = Order.objects.get(id=order_id)
            new_status = request.POST.get('status')
            
            if new_status in dict(Order.ORDER_STATUS):
                order.status = new_status
                order.save()
                
                # If order is paid, free up the table
                if new_status == 'paid':
                    order.table.status = 'available'
                    order.table.save()
                
                messages.success(request, f'Order {order.order_number} status updated to {new_status}')
            else:
                messages.error(request, 'Invalid status')
                
        except Order.DoesNotExist:
            messages.error(request, 'Order not found')
    
    return redirect('order_management')


@login_required
def create_reservation(request):
    if request.method == 'POST':
        try:
            customer_name = request.POST.get('customer_name')
            customer_phone = request.POST.get('customer_phone')
            customer_email = request.POST.get('customer_email')
            table_id = request.POST.get('table')
            reservation_date = request.POST.get('reservation_date')
            reservation_time = request.POST.get('reservation_time')
            party_size = int(request.POST.get('party_size', 1))
            special_requests = request.POST.get('special_requests', '')
            
            table = Table.objects.get(id=table_id)
            
            # Check if table is available for the requested time
            conflicting_reservation = Reservation.objects.filter(
                table=table,
                reservation_date=reservation_date,
                reservation_time=reservation_time,
                status__in=['confirmed', 'pending']
            ).exists()
            
            if conflicting_reservation:
                messages.error(request, 'This table is already reserved for the selected date and time')
            else:
                reservation = Reservation.objects.create(
                    customer_name=customer_name,
                    customer_phone=customer_phone,
                    customer_email=customer_email,
                    table=table,
                    reservation_date=reservation_date,
                    reservation_time=reservation_time,
                    party_size=party_size,
                    special_requests=special_requests,
                    status='confirmed'
                )
                
                messages.success(request, f'Reservation created successfully for {customer_name}')
                return redirect('reservation_management')
                
        except Exception as e:
            messages.error(request, f'Error creating reservation: {str(e)}')
    
    # GET request - show form
    tables = Table.objects.filter(status='available')
    
    context = {
        'tables': tables,
        'min_date': date.today().isoformat()
    }
    return render(request, 'restaurant/create_reservation.html', context)


@login_required
def update_reservation_status(request, reservation_id):
    if request.method == 'POST':
        try:
            reservation = Reservation.objects.get(id=reservation_id)
            new_status = request.POST.get('status')
            
            if new_status in dict(Reservation.RESERVATION_STATUS):
                reservation.status = new_status
                reservation.save()
                messages.success(request, f'Reservation status updated to {new_status}')
            else:
                messages.error(request, 'Invalid status')
                
        except Reservation.DoesNotExist:
            messages.error(request, 'Reservation not found')
    
    return redirect('reservation_management')


@login_required
def add_menu_item(request):
    if request.method == 'POST':
        try:
            name = request.POST.get('name')
            description = request.POST.get('description')
            price = float(request.POST.get('price', 0))
            category_id = request.POST.get('category')
            preparation_time = int(request.POST.get('preparation_time', 15))
            
            category = Category.objects.get(id=category_id)
            
            menu_item = MenuItem.objects.create(
                name=name,
                description=description,
                price=price,
                category=category,
                preparation_time=preparation_time,
                is_available=True
            )
            
            messages.success(request, f'Menu item "{name}" added successfully!')
            return redirect('menu_management')
            
        except Exception as e:
            messages.error(request, f'Error adding menu item: {str(e)}')
    
    # GET request - show form
    categories = Category.objects.all()
    
    context = {
        'categories': categories
    }
    return render(request, 'restaurant/add_menu_item.html', context)


@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    
    context = {
        'order': order
    }
    return render(request, 'restaurant/order_detail.html', context)


@login_required
def sales_report(request):
    # Simple sales report for the last 7 days
    end_date = timezone.now().date()
    start_date = end_date - timezone.timedelta(days=7)
    
    orders = Order.objects.filter(
        created_at__date__range=[start_date, end_date],
        status='paid'
    )
    
    daily_sales = []
    current_date = start_date
    while current_date <= end_date:
        day_orders = orders.filter(created_at__date=current_date)
        daily_revenue = sum(order.total_amount for order in day_orders)
        daily_sales.append({
            'date': current_date,
            'orders_count': day_orders.count(),
            'revenue': daily_revenue
        })
        current_date += timezone.timedelta(days=1)
    
    total_revenue = sum(day['revenue'] for day in daily_sales)
    total_orders = sum(day['orders_count'] for day in daily_sales)
    
    context = {
        'daily_sales': daily_sales,
        'total_revenue': total_revenue,
        'total_orders': total_orders,
        'start_date': start_date,
        'end_date': end_date
    }
    return render(request, 'restaurant/sales_report.html', context)


@login_required
def process_order_workflow(request, order_id):
    """Complete order processing workflow"""
    order = get_object_or_404(Order, id=order_id)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'start_preparing':
            order.status = 'preparing'
            order.save()
            messages.success(request, f'Order {order.order_number} is now being prepared')
            
        elif action == 'mark_ready':
            order.status = 'ready'
            order.save()
            messages.success(request, f'Order {order.order_number} is ready for serving')
            
        elif action == 'mark_served':
            order.status = 'served'
            order.save()
            messages.success(request, f'Order {order.order_number} has been served')
            
        elif action == 'process_payment':
            order.status = 'paid'
            order.table.status = 'available'  # Free up the table
            order.table.save()
            order.save()
            messages.success(request, f'Order {order.order_number} payment processed and table freed')
    
    return redirect('order_management')


@login_required
def table_update_status(request, table_id):
    if request.method == 'post':
        try:
            table = table.object.get(id=table_id)
            new_status = request.POST.get('status')

            valid_Status = ['available', 'occupied', 'reserved', 'maintenance']
            if new_status in valid_Status:
                table.status = new_status
                table.save()

                messages.success(request, f'Table {table.table_number} status updated to {new_status}')

            else:
                messages.error(request, 'Invalid table status')

        except Table.DoesNotExist:
            messages.error(request, 'Table not found')

    return redirect('table_management')   


@login_required
def edit_menu_item(request, item_id):
    menu_item = get_object_or_404(MenuItem, id=item_id)

    if request.method == 'POST':
        try:
            menu_item.name = request.POST.get('name')
            menu_item.description = request.POST.get('description')
            menu_item.price = float(request.POST.get('price', 0))
            menu_item.category_id = request.POST.get('category')
            menu_item.preparation_time = int(request.POST.get('preparation_time', 15))
            menu_item.is_available = request.POST.get('is_available') == 'on'

            menu_item.save()
            messages.success(request, f'Menu item {menu_item.name} updated successfully!')
            return redirect('menu_management')
        
        except Exception as e:
            messages.error(request, f'Error updating the menu item: {str(e)}')

    # Get request - show form
    categories = Category.objects.all()

    context = {
        'menu_item': menu_item,
        'categories': categories
    }
    return render(request, 'restaurant/edit_menu_item.html', context)


@login_required
def delete_menu_item(request, item_id):
    if request.method == 'POST':
        try:
            menu_item = MenuItem.objects.get(id=item_id)
            item_name = menu_item.name
            menu_item.delete()

            messages.success(request, f'Menu item {item_name} deleted successfully!')
        except MenuItem.DoesNotExist:
            messages.error(request, 'Menu item noyt found')

    return redirect('menu_management')
            

@login_required
def toggle_menu_availability(request, item_id):
    if request.method == 'POST':
        try:
            menu_item = MenuItem.objects.get(id=menu_item)
            menu_item.is_available = not menu_item.is_available
            menu_item.save()

            status = "available" if menu_item.is_available else "unavailable"
            messages.success(request, f'Menu item {menu_item.name} is now {status}')
        except MenuItem.DoesNotExist:
            messages.error(request, 'Menu item us not found')

    return redirect('menu_management')       


@login_required
def add_table(request):
    if request.method == 'POST':
        try:
            table_number = request.POST.get('table_number')
            capacity = int(request.POST.get('capacity', 2))
            location = request.POST.get('location', 'Main Hall')

            # Check if the table number already exists
            if Table.objects.filter(table_number=table_number).exists():
                messages.error(request, f'Table number {table_number} already exists!')
            else:
                table = Table.objects.create(
                    table_number=table_number,
                    capacity=capacity,
                    location=location,
                    status='available'
                )    
                messages.success(request, f"Table numver {table_number} added successfully!")
                return redirect('table_management')
            
        except Exception as e:
            messages.error(request, f'Error adding table: {str(e)}')

    return render(request, 'restaurant/add_table.html')


@login_required
def edit_table(request, table_id):
    table = get_object_or_404(Table, id=table_id)
    
    print(f"DEBUG: Edit table accessed - Table ID: {table_id}")
    print(f"DEBUG: Current table data - Number: {table.table_number}, Capacity: {table.capacity}, Location: {table.location}")
    
    if request.method == 'POST':
        try:
            table_number = request.POST.get('table_number')
            capacity = request.POST.get('capacity')
            location = request.POST.get('location', 'Main Hall')
            
            print(f"DEBUG: Form submitted with - Number: {table_number}, Capacity: {capacity}, Location: {location}")
            print(f"DEBUG: POST data: {request.POST}")
            
            # Check if table number already exists (excluding current table)
            if Table.objects.filter(table_number=table_number).exclude(id=table_id).exists():
                messages.error(request, f'Table number {table_number} already exists!')
                print(f"DEBUG: Table number conflict - {table_number} already exists")
            else:
                table.table_number = table_number
                table.capacity = int(capacity)
                table.location = location
                table.save()
                
                print(f"DEBUG: Table saved successfully")
                print(f"DEBUG: New table data - Number: {table.table_number}, Capacity: {table.capacity}, Location: {table.location}")
                
                messages.success(request, f'Table {table.table_number} updated successfully!')
                return redirect('table_management')
                
        except Exception as e:
            messages.error(request, f'Error updating table: {str(e)}')
            print(f"DEBUG: Error in edit_table: {str(e)}")
            import traceback
            print(f"DEBUG: Traceback: {traceback.format_exc()}")
    
    context = {
        'table': table
    }
    return render(request, 'restaurant/edit_table.html', context)


@login_required
def update_table_status(request, table_id):
    if request.method == 'POST':
        try:
            table = Table.objects.get(id=table_id)
            new_status = request.POST.get('status')

            # Validate the status
            valid_statuses = ['available', 'occupied', 'reserved', 'maintenance']
            if new_status in valid_statuses:
                table.status = new_status
                table.save()

                messages.success(request, f'Table {table.table_number} status successfully updated to {new_status}')
            else:
                messages.error(request, 'Invalid table status')

        except Table.DoesNotExist:
            messages.error(request, 'Table not found')

    return redirect('table_management')        


@login_required
def edit_reservation(request, reservation_id):
    try:
        reservation = get_object_or_404(Reservation, id=reservation_id)
        
        if request.method == 'POST':
            # Get form data
            customer_name = request.POST.get('customer_name')
            customer_phone = request.POST.get('customer_phone')
            customer_email = request.POST.get('customer_email')
            table_id = request.POST.get('table')
            reservation_date = request.POST.get('reservation_date')
            reservation_time = request.POST.get('reservation_time')
            party_size = int(request.POST.get('party_size', 1))
            special_requests = request.POST.get('special_requests', '')
            
            new_table = Table.objects.get(id=table_id)
            
            # Check for conflicts (excluding current reservation)
            conflicting_reservation = Reservation.objects.filter(
                table=new_table,
                reservation_date=reservation_date,
                reservation_time=reservation_time,
                status__in=['confirmed', 'pending']
            ).exclude(id=reservation_id).exists()
            
            if conflicting_reservation:
                messages.error(request, 'This table is already reserved for the selected date and time')
            else:
                # Update reservation
                reservation.customer_name = customer_name
                reservation.customer_phone = customer_phone
                reservation.customer_email = customer_email
                reservation.table = new_table
                reservation.reservation_date = reservation_date
                reservation.reservation_time = reservation_time
                reservation.party_size = party_size
                reservation.special_requests = special_requests
                reservation.save()
                
                messages.success(request, f'Reservation for {customer_name} updated successfully!')
                return redirect('reservation_management')
                
    except Exception as e:
        messages.error(request, f'Error updating reservation: {str(e)}')
    
    # GET request - show form with current data
    tables = Table.objects.filter(status='available')
    
    context = {
        'reservation': reservation,
        'tables': tables,
        'min_date': date.today().isoformat()
    }
    return render(request, 'restaurant/edit_reservation.html', context)


@login_required
def add_inventory_item(request):
    if request.method == 'POST':
        form = InventoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Inventory item added successfully!')
            return redirect('inventory_management')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = InventoryForm()
    
    context = {
        'form': form,
        'title': 'Add Inventory Item'
    }
    return render(request, 'restaurant/add_inventory.html', context)

@login_required
def edit_inventory_item(request, inventory_id):
    item = get_object_or_404(Inventory, id=inventory_id)
    
    if request.method == 'POST':
        form = InventoryForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            messages.success(request, f'{item.item_name} updated successfully!')
            return redirect('inventory_management')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = InventoryForm(instance=item)
    
    context = {
        'form': form,
        'item': item,
        'title': 'Edit Inventory Item'
    }
    return render(request, 'restaurant/edit_inventory.html', context)

@login_required
def restock_inventory(request, inventory_id):
    if request.method == 'POST':
        try:
            item = get_object_or_404(Inventory, id=inventory_id)
            restock_quantity = int(request.POST.get('restock_quantity', 0))
            
            if restock_quantity > 0:
                item.current_stock += restock_quantity
                item.save()
                messages.success(request, f'Added {restock_quantity} {item.unit} of {item.item_name}. New stock: {item.current_stock}')
            else:
                messages.error(request, 'Please enter a valid quantity greater than 0.')
                
        except ValueError:
            messages.error(request, 'Please enter a valid number.')
        except Exception as e:
            messages.error(request, f'Error restocking item: {str(e)}')
    
    return redirect('inventory_management')

@login_required
def delete_inventory_item(request, inventory_id):
    if request.method == 'POST':
        try:
            item = get_object_or_404(Inventory, id=inventory_id)
            item_name = item.item_name
            item.delete()
            messages.success(request, f'Inventory item "{item_name}" deleted successfully!')
        except Exception as e:
            messages.error(request, f'Error deleting item: {str(e)}')
    
    return redirect('inventory_management')

@login_required
def update_inventory(request, inventory_id):
    if request.method == 'POST':
        try:
            item = get_object_or_404(Inventory, id=inventory_id)
            action = request.POST.get('action')
            
            if action == 'set':
                # Set stock to specific value
                new_stock = int(request.POST.get('current_stock', 0))
                if new_stock >= 0:
                    item.current_stock = new_stock
                    item.save()
                    messages.success(request, f'Stock for {item.item_name} set to {new_stock}')
                else:
                    messages.error(request, 'Stock cannot be negative.')
                    
            elif action == 'add':
                # Add to current stock
                add_quantity = int(request.POST.get('current_stock', 0))
                if add_quantity > 0:
                    item.current_stock += add_quantity
                    item.save()
                    messages.success(request, f'Added {add_quantity} {item.unit} to {item.item_name}. New stock: {item.current_stock}')
                else:
                    messages.error(request, 'Please enter a quantity greater than 0.')
            
        except ValueError:
            messages.error(request, 'Please enter a valid number.')
        except Exception as e:
            messages.error(request, f'Error updating inventory: {str(e)}')
    
    return redirect('inventory_management')


@login_required
def edit_inventory_item(request, inventory_id):
    print(f"DEBUG: Edit view called for ID: {inventory_id}")
    
    try:
        item = get_object_or_404(Inventory, id=inventory_id)
        print(f"DEBUG: Found item - ID: {item.id}, Name: {item.item_name}")
    except Exception as e:
        print(f"DEBUG: Error finding item: {str(e)}")
        messages.error(request, 'Inventory item not found')
        return redirect('inventory_management')
    
    if request.method == 'POST':
        print("DEBUG: Processing POST request")
        try:
            # Update item with form data
            item.item_name = request.POST.get('item_name')
            item.category = request.POST.get('category')
            item.current_stock = float(request.POST.get('current_stock', 0))
            item.minimum_stock = float(request.POST.get('minimum_stock', 0))
            item.unit = request.POST.get('unit')
            item.cost_per_unit = float(request.POST.get('cost_per_unit', 0))
            item.save()
            
            print(f"DEBUG: Item updated successfully: {item.item_name}")
            messages.success(request, f'Inventory item "{item.item_name}" updated successfully!')
            return redirect('inventory_management')
            
        except Exception as e:
            print(f"DEBUG: Error updating item: {str(e)}")
            messages.error(request, f'Error updating inventory item: {str(e)}')
    
    print("DEBUG: Rendering edit template")
    context = {
        'item': item
    }
    return render(request, 'restaurant/edit_inventory_working.html', context)


@login_required
def add_inventory_item(request):
    print("DEBUG: Add inventory view called")
    
    if request.method == 'POST':
        print("DEBUG: Processing POST request")
        try:
            # Get form data
            item_name = request.POST.get('item_name')
            category = request.POST.get('category')
            current_stock = float(request.POST.get('current_stock', 0))
            minimum_stock = float(request.POST.get('minimum_stock', 0))
            unit = request.POST.get('unit')
            cost_per_unit = float(request.POST.get('cost_per_unit', 0))
            
            print(f"DEBUG: Creating item: {item_name}")
            
            # Create new inventory item
            inventory_item = Inventory.objects.create(
                item_name=item_name,
                category=category,
                current_stock=current_stock,
                minimum_stock=minimum_stock,
                unit=unit,
                cost_per_unit=cost_per_unit
            )
            
            messages.success(request, f'Inventory item "{item_name}" added successfully!')
            return redirect('inventory_management')
            
        except Exception as e:
            print(f"DEBUG: Error: {str(e)}")
            messages.error(request, f'Error adding inventory item: {str(e)}')
    
    print("DEBUG: Rendering add template")
    return render(request, 'restaurant/add_inventory_working.html')
