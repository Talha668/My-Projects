from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('menu/', views.menu_management, name='menu_management'),
    path('menu/add/', views.add_menu_item, name='add_menu_item'),
    path('orders/', views.order_management, name='order_management'),
    path('orders/create/', views.create_order, name='create_order'),
    path('orders/<int:order_id>/', views.order_detail, name='order_detail'),
    path('orders/<int:order_id>/update-status/', views.update_order_status, name='update_order_status'),
    path('tables/', views.table_management, name='table_management'),
    path('reservations/', views.reservation_management, name='reservation_management'),
    path('reservations/create/', views.create_reservation, name='create_reservation'),
    path('reservations/<int:reservation_id>/edit/', views.edit_reservation, name='edit_reservation'),
    path('reservations/<int:reservation_id>/update-status/', views.update_reservation_status, name='update_reservation_status'),
    path('inventory/', views.inventory_management, name='inventory_management'),
    path('inventory/add/', views.add_inventory_item, name='add_inventory_item'),
    path('inventory/<int:inventory_id>/edit/', views.edit_inventory_item, name='edit_inventory_item'),
    path('inventory/<int:inventory_id>/update/', views.update_inventory, name='update_inventory'),
    path('inventory/<int:inventory_id>/delete/', views.delete_inventory_item, name='delete_inventory_item'),
    path('inventory/<int:inventory_id>/restock/', views.restock_inventory, name='restock_inventory'),
    path('reports/sales/', views.sales_report, name='sales_report'),
    path('menu/<int:item_id>/edit/', views.edit_menu_item, name='edit_menu_item'),
    path('menu/<int:item_id>/delete/', views.delete_menu_item, name='delete_menu_item'),
    path('menu/<int:item_id>/toggle-availability/', views.toggle_menu_availability, name='toggle_menu_availability'),
    path('tables/add/', views.add_table, name='add_table'),
    path('tables/<int:table_id>/edit/', views.edit_table, name='edit_table'),
    path('tables/<int:table_id>/update-status/', views.update_table_status, name='update_table_status'),
    path('accounts/login/', auth_views.LoginView.as_view(template_name='restaurant/login.html'), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),
]