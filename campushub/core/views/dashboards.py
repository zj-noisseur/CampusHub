from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required

from ..models import Club, Event, PreRegisteredAttendee, Attendance, Committee
from django.utils import timezone
from django.db.models import Q

@login_required
def club_admin_dashboard(request, club_id):
    club = get_object_or_404(Club, id=club_id)
    # Get all events for this club
    events = Event.objects.filter(club=club).order_by('-event_date')
    
    return render(request, 'club_admin_dashboard.html', {
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
    
    # Flip the visual status on the RSVP list
    prereg.is_attended = not prereg.is_attended
    prereg.save()
    
    # PUSH TO THE OFFICIAL ATTENDANCE DATABASE TABLE
    if prereg.is_attended:
        if prereg.user:
            Attendance.objects.get_or_create(event=prereg.event, user=prereg.user)
        else:
            Attendance.objects.get_or_create(
                event=prereg.event, 
                guest_email=prereg.guest_email,
                defaults={'guest_name': prereg.guest_name}
            )
    else:
        # If toggled back to Absent, delete them from the Attendance database table
        if prereg.user:
            Attendance.objects.filter(event=prereg.event, user=prereg.user).delete()
        else:
            Attendance.objects.filter(event=prereg.event, guest_email=prereg.guest_email).delete()
            
    return redirect('core:club_admin_dashboard', club_id=prereg.event.club.id)


def student_dashboard(request):
    user = request.user
    
    # 1. Get events this user actually attended
    # Use Q to include events where the user is identified by their account OR guest email
    participated_events = Event.objects.filter(
        Q(attendances__user=user) | Q(attendances__guest_email=user.email)
    ).distinct().order_by('-event_date')
    
    # 2. Get all registrations (RSVPs) for this user (account or guest email)
    my_registrations = PreRegisteredAttendee.objects.filter(
        Q(user=user) | Q(guest_email=user.email)
    ).distinct().order_by('-event__event_date')
    
    # 3. Get clubs (Looking THROUGH the Committee and Membership tables)
    managed_clubs = Club.objects.filter(committee__user=user)
    joined_clubs = Club.objects.filter(members__user=user).exclude(committee__user=user)
    
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
def toggle_event_status(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    
    # Optional security check: make sure only the club committee can do this
    # if request.user not in event.club.committee.all():
    #     return HttpResponseForbidden("You are not authorized to do this.")
        
    event.is_finished = not event.is_finished
    event.save()
    
    # Redirect back to the admin dashboard
    return redirect('core:club_admin_dashboard', club_id=event.club.id)

def club_profile(request, club_id):
    club = get_object_or_404(Club, id=club_id)
    events = Event.objects.filter(club=club).order_by('event_date')
    
    # Check if the logged-in user is in the committee
    is_manager = False
    if request.user.is_authenticated:
        # Looking through the committee table to see if they are an active admin/manager
        is_manager = club.committee.filter(user=request.user, is_active=True).exists()
        
    context = {
        'club': club,
        'events': events,
        'is_manager': is_manager,
    }
    return render(request, 'club_profile.html', context)