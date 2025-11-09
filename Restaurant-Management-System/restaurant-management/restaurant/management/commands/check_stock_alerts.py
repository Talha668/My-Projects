from django.core.management.base import BaseCommand
from restaurant.models import Inventory, StockAlert
from django.db import models


class Command(BaseCommand):
    help = 'Check inventory and create stock alerts'
    
    def handle(self, *args, **options):
        low_stock_items = Inventory.objects.filter(
            current_stock__lte=models.F('minimum_stock')
        )
        
        for item in low_stock_items:
            # Check if alert already exists and is unresolved
            existing_alert = StockAlert.objects.filter(
                inventory=item,
                is_resolved=False
            ).exists()
            
            if not existing_alert:
                alert_type = 'out' if item.current_stock == 0 else 'low'
                message = f"{item.item_name} is {'out of' if alert_type == 'out' else 'running low on'} stock. Current: {item.current_stock} {item.unit}"
                
                StockAlert.objects.create(
                    inventory=item,
                    alert_type=alert_type,
                    message=message
                )
                
                self.stdout.write(f"Created alert: {message}")
        
        self.stdout.write(self.style.SUCCESS('Stock alert check completed'))