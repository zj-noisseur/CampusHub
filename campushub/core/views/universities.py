from django.shortcuts import render, get_object_or_404
from django.db.models import Count, Q
from core.models import Institution, State
from PIL import Image
from django.conf import settings
import os

def universities(request, state_id):
    state = get_object_or_404(State, id=state_id)
    search_query = request.GET.get('search', '').strip()

    universities = Institution.objects.filter(state=state).annotate(club_count=Count('clubs'))

    if search_query:
        universities = universities.filter(university_name__icontains=search_query)

    return render(request, 'universities.html', {'universities': universities, 'state': state})