from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required

from ..models import Club, Event, PreRegisteredAttendee, Attendance, ClubManager
from django.utils import timezone
from django.db.models import Q

@login_required
def club_admin_dashboard(request, club_id, event_id=None):
    club = get_object_or_404(Club, id=club_id)
    # Get events for this club
    if event_id:
        events = Event.objects.filter(club=club, id=event_id)
    else:
        events = Event.objects.filter(club=club).order_by('-event_date')
    
    return render(request, 'event_manage.html', {
        'club': club,
        'events': events,
    })

@login_required
def toggle_ready_status(request, event_id, prereg_id):
    prereg = get_object_or_404(PreRegisteredAttendee, id=prereg_id, event_id=event_id)
    
    prereg.is_ready = not prereg.is_ready
    prereg.save()
    
    return redirect('core:club_admin_dashboard', club_id=prereg.event.club.id)

@login_required
def toggle_attended_status(request, event_id, prereg_id):
    prereg = get_object_or_404(PreRegisteredAttendee, id=prereg_id, event_id=event_id)
    
    # We check if an Attendance record already exists to decide whether to create or delete it.
    # The PreRegisteredAttendee.is_attended status will be updated via Django signals.
    
    if prereg.user:
        attendance = Attendance.objects.filter(event=prereg.event, user=prereg.user)
    else:
        attendance = Attendance.objects.filter(event=prereg.event, guest_email=prereg.email)

    if attendance.exists():
        attendance.delete()
    else:
        if prereg.user:
            Attendance.objects.create(event=prereg.event, user=prereg.user)
        else:
            Attendance.objects.create(
                event=prereg.event, 
                guest_email=prereg.email,
                guest_name=prereg.name
            )
            
    return redirect('core:club_admin_dashboard', club_id=prereg.event.club.id)


@login_required
def student_dashboard(request):
    user = request.user
    
    # 1. Get events this user actually attended
    # Use Q to include events where the user is identified by their account OR guest email
    participated_events = Event.objects.filter(
        Q(attendances__user=user) | Q(attendances__guest_email=user.email)
    ).distinct().order_by('-event_date')
    
    # 2. Get all registrations (RSVPs) for this user (account or guest email)
    my_registrations = PreRegisteredAttendee.objects.filter(
        Q(user=user) | Q(email=user.email)
    ).distinct().order_by('-event__event_date')
    
    # 3. Get clubs (Looking THROUGH the ClubManager and Membership tables)
    managed_clubs = Club.objects.filter(managers__user=user)
    joined_clubs = Club.objects.filter(members__user=user).exclude(managers__user=user)
    
    context = {
        'user': user,
        'participated_events': participated_events,
        'my_registrations': my_registrations, # THIS WAS MISSING
        'managed_clubs': managed_clubs,
        'joined_clubs': joined_clubs,
        'today': timezone.localdate(),
    }
    
    return render(request, 'student_dashboard.html', context)

@login_required
def set_event_status(request, event_id, status):
    event = get_object_or_404(Event, id=event_id)
    
    if status.upper() in dict(Event.STATUS_CHOICES):
        event.status = status.upper()
        event.save()
    
    return redirect('core:club_admin_dashboard', club_id=event.club.id)

def club_profile(request, club_id):
    club = get_object_or_404(Club, id=club_id)
    events = Event.objects.filter(club=club).order_by('event_date')
    
    # Check if the logged-in user is in the managers
    is_manager = False
    if request.user.is_authenticated:
        # Looking through the managers table to see if they are an active admin/manager
        is_manager = club.managers.filter(user=request.user, is_active=True).exists()
        
    attended_event_ids = []
    if request.user.is_authenticated:
        attended_event_ids = list(Attendance.objects.filter(
            event__club=club,
            user=request.user
        ).values_list('event_id', flat=True))

    context = {
        'club': club,
        'events': events,
        'is_manager': is_manager,
        'is_member': club.members.filter(user=request.user, status='ACTIVE').exists() if request.user.is_authenticated else False,
        'attended_event_ids': attended_event_ids,
    }
    return render(request, 'club_profile.html', context)

@login_required
def club_settings(request, club_id):
    club = get_object_or_404(Club, id=club_id)
    
    # Check if the user is a manager
    is_manager = club.managers.filter(user=request.user, is_active=True).exists()
    if not is_manager:
        return redirect('core:club_profile', club_id=club.id)
        
    from ..forms import ClubSettingsForm
    
    if request.method == 'POST':
        form = ClubSettingsForm(request.POST, request.FILES, instance=club)
        if form.is_valid():
            form.save()
            return redirect('core:club_profile', club_id=club.id)
    else:
        form = ClubSettingsForm(instance=club)
        
    context = {
        'club': club,
        'form': form,
    }
    return render(request, 'club_settings.html', context)
