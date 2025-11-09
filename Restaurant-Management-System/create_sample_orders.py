# create_sample_orders.py (Django ORM version)
import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'restaurant_project.settings')
django.setup()

from restaurant.models import MenuItem, Table, Order, OrderItem
from django.utils import timezone

def create_sample_orders():
    print("🚀 Creating sample orders using Django ORM...")
    
    try:
        # Get menu items and tables
        caesar_salad = MenuItem.objects.get(name='Caesar Salad')
        garlic_bread = MenuItem.objects.get(name='Garlic Bread')
        grilled_salmon = MenuItem.objects.get(name='Grilled Salmon')
        chicken_parmesan = MenuItem.objects.get(name='Chicken Parmesan')
        beef_burger = MenuItem.objects.get(name='Beef Burger')
        chocolate_cake = MenuItem.objects.get(name='Chocolate Cake')
        orange_juice = MenuItem.objects.get(name='Orange Juice')
        coffee = MenuItem.objects.get(name='Coffee')
        
        table1 = Table.objects.get(table_number='T01')
        table2 = Table.objects.get(table_number='T02')
        table3 = Table.objects.get(table_number='T03')
        
    except Exception as e:
        print(f"❌ Error: Make sure you ran the sample data script first: {e}")
        return

    # Create orders directly using Django ORM
    orders_data = [
        {
            'table': table1,
            'customer_name': 'John Smith',
            'items': [
                {'menu_item': caesar_salad, 'quantity': 2, 'unit_price': caesar_salad.price},
                {'menu_item': grilled_salmon, 'quantity': 1, 'unit_price': grilled_salmon.price},
                {'menu_item': orange_juice, 'quantity': 2, 'unit_price': orange_juice.price},
            ]
        },
        {
            'table': table2,
            'customer_name': 'Sarah Johnson',
            'items': [
                {'menu_item': garlic_bread, 'quantity': 1, 'unit_price': garlic_bread.price},
                {'menu_item': chicken_parmesan, 'quantity': 2, 'unit_price': chicken_parmesan.price},
                {'menu_item': chocolate_cake, 'quantity': 1, 'unit_price': chocolate_cake.price},
                {'menu_item': coffee, 'quantity': 2, 'unit_price': coffee.price},
            ]
        },
        {
            'table': table3,
            'customer_name': 'Mike Wilson',
            'items': [
                {'menu_item': beef_burger, 'quantity': 3, 'unit_price': beef_burger.price},
                {'menu_item': orange_juice, 'quantity': 3, 'unit_price': orange_juice.price},
            ]
        }
    ]
    
    for order_data in orders_data:
        try:
            # Create order
            order = Order.objects.create(
                table=order_data['table'],
                customer_name=order_data['customer_name'],
                status='confirmed'
            )
            
            # Create order items
            total_amount = 0
            for item_data in order_data['items']:
                order_item = OrderItem.objects.create(
                    order=order,
                    menu_item=item_data['menu_item'],
                    quantity=item_data['quantity'],
                    unit_price=item_data['unit_price']
                )
                total_amount += order_item.total_price
            
            # Update order total
            order.total_amount = total_amount
            order.save()
            
            print(f"✅ Order created: {order.order_number} - ${order.total_amount}")
            
        except Exception as e:
            print(f"❌ Error creating order: {e}")

if __name__ == '__main__':
    create_sample_orders()
    print("🎉 Sample orders creation completed!")