from django.shortcuts import render, get_object_or_404
from django.db.models import Count
from core.models import Institution, State
from PIL import Image
from django.conf import settings
import os

def universities(request, state_id):
    state = get_object_or_404(State, id=state_id)
    universities = Institution.objects.filter(state=state).annotate(club_count=Count('clubs'))

    # target_width = None

    # for university in universities:
    #     if university.logo:
    #         logo_path = os.path.join(settings.MEDIA_ROOT, university.logo.name)
    #         try:
    #             with Image.open(logo_path) as img:
    #                 if target_width is None or img.width < target_width:
    #                     target_width = img.width
    #         except FileNotFoundError:
    #             continue

    # target_width = target_width or 100


    return render(request, 'universities.html', {'universities': universities, 'state': state})