from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
# Create your models here.


class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class MenuItem(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='menu_items/', blank=True, null=True)
    is_available = models.BooleanField(default=True)
    preparation_time = models.IntegerField(help_text="Preparation time in minutes")

    def __str__(self):
        return self.name


class Table(models.Model):
    TABLE_STATUS = [
        ('available', 'Available'),
        ('occupied', 'Occupied'),
        ('reserved', 'Reserved'),
        ('maintenance', 'Maintenance'),
    ]
    
    table_number = models.CharField(max_length=10, unique=True)
    capacity = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(20)])
    status = models.CharField(max_length=20, choices=TABLE_STATUS, default='available')
    location = models.CharField(max_length=100, help_text="e.g., 'Window Side', 'Garden View'")
    created_at = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return f"Table {self.table_number} ({self.capacity} persons)"


class Reservation(models.Model):
    RESERVATION_STATUS = [
        ('confirmed', 'Confirmed'),
        ('pending', 'Pending'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    ]
    
    customer_name = models.CharField(max_length=200)
    customer_phone = models.CharField(max_length=15)
    customer_email = models.EmailField()
    table = models.ForeignKey(Table, on_delete=models.CASCADE)
    reservation_date = models.DateField()
    reservation_time = models.TimeField()
    party_size = models.IntegerField(validators=[MinValueValidator(1)])
    status = models.CharField(max_length=20, choices=RESERVATION_STATUS, default='confirmed')
    special_requests = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Reservation for {self.customer_name} on {self.reservation_date}"


class Order(models.Model):
    ORDER_STATUS = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('preparing', 'Preparing'),
        ('ready', 'Ready'),
        ('served', 'Served'),
        ('cancelled', 'Cancelled'),
        ('paid', 'Paid'),
    ]
    
    order_number = models.CharField(max_length=20, unique=True)
    table = models.ForeignKey(Table, on_delete=models.CASCADE)
    customer_name = models.CharField(max_length=200, blank=True)
    status = models.CharField(max_length=20, choices=ORDER_STATUS, default='pending')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    notes = models.TextField(blank=True)
    
    def save(self, *args, **kwargs):
        if not self.order_number:
            # Generate order number: ORD-YYYYMMDD-XXXX
            date_str = timezone.now().strftime('%Y%m%d')
            last_order = Order.objects.filter(order_number__startswith=f'ORD-{date_str}').order_by('order_number').last()
            if last_order:
                last_num = int(last_order.order_number.split('-')[-1])
                new_num = last_num + 1
            else:
                new_num = 1
            self.order_number = f'ORD-{date_str}-{new_num:04d}'
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.order_number


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.IntegerField(validators=[MinValueValidator(1)])
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    special_instructions = models.TextField(blank=True, null=True)
    notes = models.TextField(blank=True)
    
    @property
    def total_price(self):
        return self.quantity * self.unit_price
    
    def __str__(self):
        return f"{self.quantity} x {self.menu_item.name}"

    def save(self, *args, **kwargs):
        # Auto update the inventory when the order item is created
        if not self.pk:   # Only on creation
            self.update_inventory()
        super().save(*args, **kwargs)

    def update_inventorty(self):
        """Update inventory based on recipee ingrediants"""
        try:
            ingredients_to_update = {
                'Tomato': 0.1 * self.quantity,
                'Onion': 0.05 * self.quantity,
                'Cooking Oil': 0.02 * self.quantity,
            }

            for item_name, quantity_used in ingredients_to_update.items():
                try:
                    inventory_item = Inventory.objects.get(item_name=item_name)
                    inventory_item.current_stock -= quantity_used
                    inventory_item.save()
                except Inventory.DoesNotExist:
                    pass  # If ingredients does not exists

        except Exception as e:
            # Log error but does not break the order
            print(f"Inventory update error: {e}") 

    def save(self, *args, **kwargs):
        # Auto update items when order item is created 
        if not self.pk:
            self.update_inventorty()
        super().save(*args, **kwargs)

    def update_inventory(self):
        """Update inventory based on menu items"""
        try:
            ingredient_mapping = {
                'Caeser salad': {'Tomatoes': 0.2, 'Bread': 0.1},
                'Grilled Salmon': {'Salmon': 0.3},
                'Chicken Parmesan': {'Chicken Breast': 0.25},
                'Beef Burger': {'Beef': 0.2, 'Bread': 0.1},
                'Garlic Bread': {'Bread': 0.2},
            }
            
            item_name = self.menu_item.name
            if item_name in ingredient_mapping:
                for ingredient, quantity_used in ingredient_mapping[item_name].items():
                    try:
                        inventory_item = Inventory.objects.get(item_name=ingredient)
                        total_used = quantity_used * self.quantity
                        inventory_item.current_stock = max(0, inventory_item.current_stock - total_used)
                        inventory_item.save()
                    except Inventory.DoesNotExist:
                        continue
                        
        except Exception as e:
            print(f"Inventory update error: {e}")                         


class Inventory(models.Model):
    CATEGORY_CHOICES = [
        ('vegetables', 'Vegetables'),
        ('fruits', 'Fruits'),
        ('meat', 'Meat'),
        ('seafood', 'Seafood'),
        ('dairy', 'Dairy'),
        ('grains', 'Grains'),
        ('spices', 'Spices'),
        ('beverages', 'Beverages'),
        ('cleaning', 'Cleaning Supplies'),
        ('other', 'Other'),
    ]
    
    UNIT_CHOICES = [
        
        ('kg', 'Kilogram'),
        ('g', 'Gram'),
        ('lb', 'Pound'),
        ('oz', 'Ounce'),
        ('l', 'Liter'),
        ('ml', 'Milliliter'),
        ('piece', 'Piece'),
        ('pack', 'Pack'),
        ('bottle', 'Bottle'),
        ('can', 'Can'),
    ]

    item_name = models.CharField(max_length=100)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    current_stock = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    minimum_stock = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    unit = models.CharField(max_length=10, choices=UNIT_CHOICES)
    cost_per_unit = models.DecimalField(max_digits=10, decimal_places=2)
    supplier_info = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.item_name} ({self.current_stock} {self.unit})"
    
    class Meta:
        verbose_name_plural = "Inventory"


class SalesReport(models.Model):
    report_date = models.DateField(unique=True)
    total_orders = models.IntegerField(default=0)
    total_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_customers = models.IntegerField(default=0)
    average_order_value = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Sales Report - {self.report_date}"


class Recipe(models.Model):
    """Map menu items to ingredients for accurate inventory tracking"""
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    ingredient = models.ForeignKey('Inventory', on_delete=models.CASCADE)
    quantity_required = models.DecimalField(max_digits=10, decimal_places=2)
    unit = models.CharField(max_length=20)
    
    def __str__(self):
        return f"{self.menu_item.name} - {self.ingredient.item_name}"


class StockAlert(models.Model):
    """Track stock alerts"""
    inventory = models.ForeignKey('Inventory', on_delete=models.CASCADE)
    alert_type = models.CharField(max_length=20, choices=[('low', 'Low Stock'), ('out', 'Out of Stock')])
    message = models.TextField()
    is_resolved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.alert_type} - {self.inventory.item_name}"
    