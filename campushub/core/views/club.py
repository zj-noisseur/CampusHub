from django.shortcuts import render
from django.views import View
from core.models import Club

class ClubView(View):
    def get(self, request):
        clubs = Club.objects.all()
        return render(request, 'core/club_list.html', {'clubs': clubs})