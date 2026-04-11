from django.shortcuts import render
from core.models import Club, Institution, State

def feed(request):
    # the user would have selected the state and the corresponding university before reaching this page

    