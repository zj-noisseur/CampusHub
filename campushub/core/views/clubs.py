from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from core.models import Club, Membership
from django.contrib import messages

@login_required
def join_club(request, club_id):
    if request.method == 'POST':
        target_club = get_object_or_404(Club, id=club_id)

        if Membership.objects.filter(user=request.user, club=target_club).exists():
            messages.warning(request, f"You are already a applied to {target_club.name}.")

        else:
            Membership.objects.create(user=request.user, club=target_club)
            messages.success(request, f"Your application to {target_club.name} has been sent.")

    return redirect(request.META.get('HTTP_REFERER', 'home'))