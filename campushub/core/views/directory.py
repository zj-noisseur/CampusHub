from django.shortcuts import get_object_or_404, render
from core.models import State, Institution
from PIL import Image
from django.conf import settings
from django.db.models import Q
import os

def directory(request):
    search_query = request.GET.get('search', '').strip()
    # Reverse relationship to get all institutions for each state
    institutions = Institution.objects.select_related('state')

    if search_query:
        institutions = institutions.filter(
            Q(university_name__icontains=search_query) | Q(state__name__icontains=search_query)
        )

    # Ensure institutions is not empty when no search query is provided
    return render(request, 'directory.html', {'institutions': institutions})