from django.shortcuts import render
from core.models import Club

def base(request):
    clubs = Club.objects.all()
    return render(request, 'base.html', {'clubs': clubs})