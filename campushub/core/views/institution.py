from django.shortcuts import render
from django.views import View
from core.models import Institution

class InstitutionView(View):
    def get(self, request):
        institutions = Institution.objects.all()
        return render(request, 'core/institution_list.html', {'institutions': institutions})