from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'categories', views.CategoryViewSet)
router.register(r'menu-items', views.MenuItemViewSet)
router.register(r'tables', views.TableViewSet)
router.register(r'reservations', views.ReservationViewSet)
router.register(r'orders', views.OrderViewSet)
router.register(r'inventory', views.InventoryViewSet)
router.register(r'reports', views.SalesReportViewSet)

urlpatterns = [
    path('', include(router.urls)),
]