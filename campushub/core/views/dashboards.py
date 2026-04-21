from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required

from ..models import Club, Event, PreRegisteredAttendee, Attendance

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