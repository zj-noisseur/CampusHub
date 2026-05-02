from django.shortcuts import redirect, get_object_or_404,render
from django.contrib.auth.decorators import login_required
from core.models import Club, Membership, ClaimRequest
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

@login_required
def apply_manager(request, club_id):
    target_club = get_object_or_404(Club, id=club_id)

    if request.method == 'POST':
        designation = request.POST.get('claimer_designation')
        proof = request.FILES.get('proof_document')

        if designation and proof:
            ClaimRequest.objects.create(
                club=target_club,
                user=request.user,
                claimer_designation=designation,
                proof_document=proof
            )

            messages.success(request, f"Success! Your application to manage {target_club.name} has been sent.")

            return redirect('core:club_profile', club_id=target_club.id)
        else:
            messages.error(request, "Please provide both your designation and proof document.")

    return render(request, 'apply_manager.html', {'club': target_club})