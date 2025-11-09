from django.urls import path
from . import views

urlpatterns = [
    path('', views.event_list, name='event-list'),
    path('event/<int:pk>/', views.event_detail, name='event-detail'),
    path('event/<int:pk>/register/', views.register_for_event, name='register-event'),
    path('my-registrations/', views.my_registrations, name='my-registrations'),
    path('registration/<int:pk>/cancel/', views.cancel_registration, name='cancel-registration'),
    path('registration/<int:pk>/success/', views.registration_success, name='registration-success'),
]