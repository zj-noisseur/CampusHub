from django.shortcuts import redirect, get_object_or_404,render
from django.contrib.auth.decorators import login_required
from core.models import Club, Membership, ClaimRequest, NewClubRequest, Institution
from django.contrib import messages

@login_required
def join_club(request, club_id):
    if request.method != 'POST':

        messages.error(request, "Oops! The form submission broke. Please try clicking 'Join' again.")
        return redirect('core:club_profile', club_id=club_id)
    
    # 1. Grab the club and keep the variable name consistently as 'club'
    club = get_object_or_404(Club, id=club_id)
    
    # 2. SAFETY CHECK: Did they already apply? Check this BEFORE saving anything!
    if Membership.objects.filter(user=request.user, club=club).exists():
        messages.warning(request, f"You have already applied to {club.name}.")
        return redirect(request.META.get('HTTP_REFERER', 'core:profile'))

    # 3. Decide the type based on the fee
    mem_type = 'UNLIMITED' if club.membership_fee > 0 else 'LIMITED'

    # 4. Create the new membership instance
    membership = Membership(
        user=request.user,
        club=club,
        membership_type=mem_type,
        status='PENDING'
    )

    # 5. If it's a paid club, grab the uploaded image using your exact field name
    if club.membership_fee > 0:
        membership.payment_proof = request.FILES.get('payment_proof')
            
    # 6. Finally, save it!
    membership.save() 
        
    messages.success(request, f"Your request to join {club.name} has been sent!")

    # Redirect them back to wherever they came from
    return redirect(request.META.get('HTTP_REFERER', 'core:home'))

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

@login_required
def propose_club(request):
    # 1. Block GET requests
    if request.method != 'POST':
        messages.error(request, "Oops! The form submission broke. Please try again.")
        return redirect(request.META.get('HTTP_REFERER', 'core:directory'))

    # 2. Extract data from the form
    institution_id = request.POST.get('institution')
    club_name = request.POST.get('club_name', '').strip()
    category = request.POST.get('category')
    description = request.POST.get('description', '').strip()

    if not all([institution_id, club_name, category, description]):
        messages.error(request, "Please fill in all required fields.")
        return redirect(request.META.get('HTTP_REFERER', 'core:directory'))

    institution = get_object_or_404(Institution, id=institution_id)

    # 3. SAFETY CHECK: Does this club already exist?
    if Club.objects.filter(institution=institution, name__iexact=club_name).exists():
        messages.warning(request, f"A club named '{club_name}' already exists at {institution.university_name}.")
        return redirect(request.META.get('HTTP_REFERER', 'core:directory'))

    # 4. SAFETY CHECK: Is someone else already proposing this exact club?
    if NewClubRequest.objects.filter(institution=institution, club_name__iexact=club_name, status='PENDING').exists():
        messages.warning(request, f"A proposal for '{club_name}' at {institution.university_name} is already under review.")
        return redirect(request.META.get('HTTP_REFERER', 'core:directory'))

    # 5. Create the proposal in the waiting room!
    NewClubRequest.objects.create(
        requester=request.user,
        institution=institution,
        club_name=club_name,
        category=category,
        description=description
    )

    messages.success(request, f"Your proposal for '{club_name}' has been submitted! You will be granted Root Admin access upon approval.")
    return redirect(request.META.get('HTTP_REFERER', 'core:directory'))