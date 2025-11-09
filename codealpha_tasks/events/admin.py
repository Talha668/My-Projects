from django.contrib import admin
from .models import Event, Registration
# Register your models here.

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['title', 'event_type', 'date', 'location', 'max_participants', 'current_participants', 'is_active']
    list_filter = ['event_type', 'date', 'is_active']
    search_fields = ['title', 'description', 'location']
    list_editable = ['is_active']


@admin.register(Registration)
class RegistrationAdmin(admin.ModelAdmin):
    list_display = ['user', 'event', 'registration_date', 'status']
    list_filter = ['status', 'registration_date']
    search_fields = ['user__username', 'event__title']