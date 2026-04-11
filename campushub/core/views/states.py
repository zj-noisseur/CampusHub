from django.shortcuts import render
from core.models import Institution, State

def states(request):
    states = State.objects.all()
    return render(request, 'states.html', {'states': states})