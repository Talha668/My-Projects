# test_data.py
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'restaurent_project.settings')
django.setup()

from restaurant.models import *

def check_all_data():
    print("🔍 Checking all data in database...")
    
    print(f"\n📊 MENU ITEMS: {MenuItem.objects.count()}")
    for item in MenuItem.objects.all():
        print(f"   - {item.name} (${item.price})")
    
    print(f"\n📊 TABLES: {Table.objects.count()}")
    for table in Table.objects.all():
        print(f"   - {table.table_number} ({table.capacity} persons) - {table.status}")
    
    print(f"\n📊 ORDERS: {Order.objects.count()}")
    for order in Order.objects.all():
        print(f"   - {order.order_number}: {order.customer_name} - ${order.total_amount} - {order.status}")
        for item in order.items.all():
            print(f"     * {item.quantity}x {item.menu_item.name} - ${item.unit_price} each")
    
    print(f"\n📊 INVENTORY: {Inventory.objects.count()}")
    for inv in Inventory.objects.all():
        print(f"   - {inv.item_name}: {inv.current_stock} {inv.unit} (min: {inv.minimum_stock})")
    
    print(f"\n📊 CATEGORIES: {Category.objects.count()}")
    for cat in Category.objects.all():
        print(f"   - {cat.name}")

if __name__ == '__main__':
    check_all_data()