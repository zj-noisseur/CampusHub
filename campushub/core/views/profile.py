from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required(login_url='/admin/login/')
def user_profile(request):
    return render(request, 'core/profile.html')