from django.shortcuts import render, get_object_or_404
from core.models import Club, Institution, State

def clubs(request, university_id, state_id):
    state = get_object_or_404(State, id=state_id)
    university = get_object_or_404(Institution, id=university_id)
    clubs = Club.objects.filter(institution=university)
    return render(request, 'clubs.html', {'clubs': clubs, 'university':university, 'state':state})