# create_sample_orders.py
import os
import django
import requests
import json

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'restaurent_project.settings')
django.setup()

from restaurant.models import MenuItem, Table

# Base URL for API
BASE_URL = 'http://127.0.0.1:8000/api'

def create_sample_orders():
    print("🚀 Creating sample orders...")
    
    try:
        # Get menu items and tables (they should exist from our previous setup)
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

    # Sample orders data
    orders_data = [
        {
            'table': table1.id,
            'customer_name': 'John Smith',
            'items': [
                {'menu_item': caesar_salad.id, 'quantity': 2},
                {'menu_item': grilled_salmon.id, 'quantity': 1},
                {'menu_item': orange_juice.id, 'quantity': 2},
            ]
        },
        {
            'table': table2.id,
            'customer_name': 'Sarah Johnson',
            'items': [
                {'menu_item': garlic_bread.id, 'quantity': 1},
                {'menu_item': chicken_parmesan.id, 'quantity': 2},
                {'menu_item': chocolate_cake.id, 'quantity': 1},
                {'menu_item': coffee.id, 'quantity': 2},
            ]
        },
        {
            'table': table3.id,
            'customer_name': 'Mike Wilson',
            'items': [
                {'menu_item': beef_burger.id, 'quantity': 3},
                {'menu_item': orange_juice.id, 'quantity': 3},
            ]
        }
    ]
    
    for order_data in orders_data:
        try:
            response = requests.post(f'{BASE_URL}/orders/', json=order_data)
            if response.status_code == 201:
                order = response.json()
                print(f"✅ Order created: {order['order_number']} - ${order['total_amount']}")
            else:
                print(f"❌ Failed to create order: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == '__main__':
    create_sample_orders()
    print("🎉 Sample orders creation completed!")