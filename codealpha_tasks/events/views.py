from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import Event, Registration
from .forms import RegistrationForm


def event_list(request):
    events = Event.objects.filter(is_active=True).order_by('date')
    return render(request, 'events/event_list.html', {'events': events})


def event_detail(request, pk):
    event = get_object_or_404(Event, pk=pk, is_active=True)
    is_registered = False
    if request.user.is_authenticated:
        is_registered = Registration.objects.filter(
            user=request.user, 
            event=event, 
            status='registered'
        ).exists()

    # Calculate Available Spots
    available_spots = event.max_participants - event.current_participants    
    
    return render(request, 'events/event_detail.html', {
        'event': event,
        'is_registered': is_registered,
        'available_spots': event.available_spots()
    })


@login_required
def register_for_event(request, pk):
    event = get_object_or_404(Event, pk=pk, is_active=True)
    
    # Check if already REGISTERED (not cancelled)
    existing_registration = Registration.objects.filter(
        user=request.user, 
        event=event,
        status='registered'  # Only check active registrations
    ).first()
    
    if existing_registration:
        messages.warning(request, 'You are already registered for this event!')
        return redirect('event-detail', pk=pk)
    
    # Check if event is full
    if event.is_full():
        messages.error(request, 'This event is already full!')
        return redirect('event-detail', pk=pk)
    
    registration = None
    
    # Check if there's a cancelled registration we can reactivate
    cancelled_registration = Registration.objects.filter(
        user=request.user,
        event=event,
        status='cancelled'
    ).first()
    
    if cancelled_registration:
        # Reactivate the cancelled registration
        cancelled_registration.status = 'registered'
        cancelled_registration.save()
        registration = cancelled_registration
    else:
        # Create new registration
        registration = Registration.objects.create(
            user=request.user,
            event=event,
            status='registered'
        )
    
    # Update event participant count
    event.current_participants += 1
    event.save()
    
    messages.success(request, f'Successfully registered for {event.title}!')
    
    return redirect('registration-success', pk=registration.pk)  # Redirect to registrations page directly


@login_required
def my_registrations(request):
    registrations = Registration.objects.filter(
        user=request.user, 
        status='registered'
    ).select_related('event').order_by('-registration_date')
    
    return render(request, 'events/my_registrations.html', {
        'registrations': registrations
    })


@login_required
def cancel_registration(request, pk):
    registration = get_object_or_404(Registration, pk=pk, user=request.user)
    
    if request.method == 'POST':
        # Only proceed if currently registered (not already cancelled)
        if registration.status == 'registered':
            registration.status = 'cancelled'
            registration.save()
        
            # Update event participant count
            event = registration.event
            if event.current_participants > 0:
                event.current_participants -= 1
                event.save()
        
            messages.success(request, 'Registration cancelled successfully!')
        else:
            messages.warning(request, 'Registration was already cancelled!')

        return redirect('my-registrations')
    
    return render(request, 'events/cancel_registration.html', {
        'registration': registration
    })


@login_required
def registration_success(request, pk):
    registration = get_object_or_404(Registration, pk=pk, user=request.user)
    return render(request, 'events/registration_success.html', {
        'registration': registration
    })
