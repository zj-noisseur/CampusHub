from django.shortcuts import render
from core.models import Institution, State

def states(request):
    # recerse relationship to get all institutions for each state
    # to be read up on !
    states = State.objects.prefetch_related('institution_set').all()
    return render(request, 'states.html', {'states': states})