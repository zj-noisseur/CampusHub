from django.shortcuts import render
from django.db.models import Count
from django.contrib.auth.decorators import login_required

from ..models import Event, Attendance

def event_dashboard(request):
    events = Event.objects.annotate(attendee_count=Count('attendances'))
    return render(request, 'dashboard.html', {'events': events})

def club_admin_dashboard(request):
    events = Event.objects.all()
    return render(request, 'club_admin_dashboard.html', {'events': events})

@login_required
def student_dashboard(request):
    my_attendances = Attendance.objects.filter(user=request.user)
    return render(request, 'student_dashboard.html', {'attendances': my_attendances})