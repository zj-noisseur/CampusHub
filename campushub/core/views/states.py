from django.shortcuts import render
from core.models import State
from PIL import Image
from django.conf import settings
import os

def states(request):
    # recerse relationship to get all institutions for each state
    # to be read up on !
    states = State.objects.prefetch_related('institution_set').all()
    # # some images uploaded have slightly smaller dimensions, treat this as the limiting factor and make sure all other images are resized this maximum dimension
    # target_width = None

    # for state in states:
    #     if state.flag:
    #         flag_path = os.path.join(settings.MEDIA_ROOT, state.flag.name)
    #         try:
    #             with Image.open(flag_path) as img:
    #                 if target_width is None or img.width < target_width:
    #                     target_width = img.width
    #         except FileNotFoundError:
    #             continue

    # target_width = target_width or 100

    return render(request, 'states.html', {'states': states})