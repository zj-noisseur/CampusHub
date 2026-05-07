from django.shortcuts import render, get_object_or_404
from core.models import Club, Institution, State
from django.db.models import Q

def clubs(request, university_id, state_id):
    state = get_object_or_404(State, id=state_id)
    university = get_object_or_404(Institution, id=university_id)
    search_query = request.GET.get('search', '').strip()

    clubs = Club.objects.filter(institution=university)

    if search_query:
        clubs = clubs.filter(name__icontains=search_query)

    return render(request, 'clubs.html', {'clubs': clubs, 'university': university, 'state': state})
