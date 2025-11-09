from django.contrib import admin
from .models import *
from django.utils import timezone
from datetime import timedelta

# Register your models here.

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'description']
    search_fields = ['name']


@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'is_available']
    list_filter = ['category', 'is_available']
    search_fields = ['name']


@admin.register(Table)
class TableAdmin(admin.ModelAdmin):
    list_display = ['table_number', 'capacity', 'status', 'location']
    list_filter = ['status', 'location']
    search_fields = ['table_number']


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ['customer_name', 'table', 'reservation_date', 'reservation_time', 'status']
    list_filter = ['status', 'reservation_date']
    search_fields = ['customer_name', 'customer_phone']


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'table', 'customer_name', 'status', 'total_amount', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['order_number', 'customer_name']
    inlines = [OrderItemInline]


@admin.register(Inventory)
class InventoryAdmin(admin.ModelAdmin):
    list_display = ['item_name', 'category', 'current_stock', 'minimum_stock', 'needs_restock']
    list_filter = ['category']
    search_fields = ['item_name']

    def needs_restock(self, obj):
        return obj.needs_restock
    needs_restock.boolean = True
    needs_restock.short_description = 'Needs Restock'


@admin.register(SalesReport)
class SalesReportAdmin(admin.ModelAdmin):
    list_display = ['report_date', 'total_orders', 'total_revenue', 'average_order_value']
    readonly_fields = ['total_orders', 'total_revenue', 'total_customers', 'average_order_value']


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ['menu_item', 'ingredient', 'quantity_required', 'unit']
    list_filter = ['menu_item', 'ingredient']


@admin.register(StockAlert)
class StockAlertAdmin(admin.ModelAdmin):
    list_display = ['inventory', 'alert_type', 'is_resolved', 'created_at']
    list_filter = ['alert_type', 'is_resolved']
    list_filter = ['alert_type', 'is_resolved']
    
    def mark_resolved(self, request, queryset):
        updated = queryset.update(is_resolved=True, resolved_at=timezone.now())
        self.message_user(request, f'{updated} alerts marked as resolved.')
    mark_resolved.short_description = "Mark selected alerts as resolved"
    actions = ['mark_resolved']
# Add dashboard to admin
admin.site.site_header = "Restaurant Management System"
admin.site.index_title = "Dashboard"
admin.site.site_title = "Restaurant Admin"