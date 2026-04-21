from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from ..models import Club, Committee, Institution

@login_required
def club_profile(request):
    # Fetch clubs where the user is an active committee member
    my_committees = Committee.objects.filter(user=request.user, is_active=True)
    
    # THE FIX: Point directly to 'club_profile.html'
    return render(request, 'club_profile.html', {'committees': my_committees})

@login_required
def create_club(request):
    institutions = Institution.objects.all()
    
    if request.method == 'POST':
        name = request.POST.get('name')
        ig_handle = request.POST.get('ig_handle')
        institution_id = request.POST.get('institution')
        
        institution = get_object_or_404(Institution, id=institution_id)
        
        new_club = Club.objects.create(
            name=name,
            ig_handle=ig_handle,
            institution=institution
        )
        
        # Automatically make the creator the Root Admin of the new club
        Committee.objects.create(
            user=request.user,
            club=new_club,
            designation="President",
            is_root=True,
            is_active=True
        )
        return redirect('core:club_profile')
        
    # THE FIX: Point directly to 'club_form.html'
    return render(request, 'club_form.html', {'institutions': institutions})

@login_required
def modify_club(request, club_id):
    # Ensure only active root members can edit
    committee_link = get_object_or_404(Committee, user=request.user, club_id=club_id, is_active=True, is_root=True)
    club = committee_link.club
    institutions = Institution.objects.all()

    if request.method == 'POST':
        club.name = request.POST.get('name')
        club.ig_handle = request.POST.get('ig_handle')
        club.institution_id = request.POST.get('institution')
        club.save()
        return redirect('core:club_profile')

    # THE FIX: Point directly to 'club_form.html'
    return render(request, 'club_form.html', {'club': club, 'institutions': institutions})