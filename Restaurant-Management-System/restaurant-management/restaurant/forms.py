# forms.py
from django import forms
from .models import Reservation, Table
from django.utils import timezone
import datetime

class ReservationForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = [
            'customer_name', 
            'customer_phone', 
            'customer_email', 
            'table', 
            'reservation_date', 
            'reservation_time', 
            'party_size', 
            'special_requests'
        ]
        widgets = {
            'reservation_date': forms.DateInput(attrs={'type': 'date', 'min': timezone.now().date()}),
            'reservation_time': forms.TimeInput(attrs={'type': 'time'}),
            'special_requests': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only show available tables
        self.fields['table'].queryset = Table.objects.filter(status='available')
        
    def clean(self):
        cleaned_data = super().clean()
        reservation_date = cleaned_data.get('reservation_date')
        reservation_time = cleaned_data.get('reservation_time')
        table = cleaned_data.get('table')
        party_size = cleaned_data.get('party_size')
        
        # Check if table is available for the requested time
        if reservation_date and reservation_time and table:
            # Check for overlapping reservations for the same table
            overlapping_reservations = Reservation.objects.filter(
                table=table,
                reservation_date=reservation_date,
                status__in=['pending', 'confirmed']
            ).exclude(pk=self.instance.pk if self.instance else None)
            
            if overlapping_reservations.exists():
                raise forms.ValidationError(
                    f"Table {table.table_number} is already reserved for this date and time."
                )
        
        # Check if party size fits table capacity
        if table and party_size:
            if party_size > table.capacity:
                raise forms.ValidationError(
                    f"Table {table.table_number} can only accommodate {table.capacity} persons."
                )
        
        return cleaned_data
    

# forms.py
from django import forms
from .models import Inventory

class InventoryForm(forms.ModelForm):
    class Meta:
        model = Inventory
        fields = [
            'item_name', 
            'category', 
            'current_stock', 
            'minimum_stock', 
            'unit', 
            'cost_per_unit',
            'supplier_info'
        ]
        widgets = {
            'item_name': forms.TextInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'current_stock': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'minimum_stock': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'unit': forms.Select(attrs={'class': 'form-control'}),
            'cost_per_unit': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'step': '0.01'}),
            'supplier_info': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }    