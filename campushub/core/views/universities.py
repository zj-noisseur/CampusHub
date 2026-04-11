from django.shortcuts import render, get_object_or_404
from core.models import Institution, State

def universities(request, state_id):
    state = get_object_or_404(State, id=state_id)
    universities = Institution.objects.filter(state=state)
    return render(request, 'universities.html', {'universities': universities, 'state': state})