from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from core.models import Club, Membership
from ..forms import ClubSettingsForm
from datetime import date
from django.utils import timezone

@login_required
def manager_dashboard(request, club_id):
    # Fetch the club(s) this specific user manages. 
    managed_clubs = Club.objects.filter(managers__user=request.user)
    
    if not managed_clubs.exists():
        messages.error(request, 'You do not have permission to view the manager dashboard.')
        return redirect('core:profile')
        
    # Get the specific club using the club_id passed in the URL
    my_club = get_object_or_404(Club, id=club_id)
    
    # Get all the students who have applied or joined this club
    memberships = Membership.objects.filter(club=my_club)

    approved_members = memberships.filter(status='APPROVED')
    pending_members = memberships.filter(status='PENDING')
    
    context = {
        'club': my_club,
        'approved_members': approved_members,
        'pending_members': pending_members,
        'total_members': approved_members.count(),
        'pending_requests': pending_members.count(),
    }
    
    # FIX #1: We RENDER the HTML template here, we don't redirect!
    return render(request, 'manager_dashboard.html', context)


@login_required
def process_membership(request, membership_id, action):
    # 1. Grab the specific membership request
    membership = get_object_or_404(Membership, id=membership_id)
    
    # 2. Security Check: Is the person clicking this actually the manager?
    if not membership.club.managers.filter(user=request.user).exists():
        messages.error(request, 'You do not have permission to manage this club.')
        # FIX #2: Added the club_id so it doesn't crash here
        return redirect('core:manager_dashboard', club_id=membership.club.id)
        
    # 3. Process the action
    if action == 'approve':
        membership.status = 'APPROVED'

        today = date.today()
        policy = membership.club.renew_policy
        if policy == 'ROLLING':
            membership.expires_at = today + timezone.timedelta(days=365)
            
        elif policy == 'CALENDAR':
            membership.expires_at = date(today.year, 12, 31)
            
        elif policy == 'LIFETIME':
            membership.expires_at = None

        membership.save()
        messages.success(request, f'Approved {membership.user.student_name}!')
    elif action == 'reject':
        membership.status = 'REJECTED'
        membership.save()
        messages.success(request, 'Membership request rejected.')
        
    # FIX #3: Added the club_id so it safely refreshes the dashboard!
    return redirect('core:manager_dashboard', club_id=membership.club.id)

@login_required
def update_club_settings(request, club_id):
    club = get_object_or_404(Club, id=club_id)
    
    if not club.managers.filter(user=request.user).exists():
        messages.error(request, 'You do not have permission to edit settings.')
        return redirect('core:profile')

    if request.method == 'POST':
        new_policy = request.POST.get('renewal_policy')
        
        valid_policies = dict(Club.RENEWAL_CHOICES).keys()
        if new_policy in valid_policies:
            club.renewal_policy = new_policy
            club.save()
            messages.success(request, f"{club.name} settings updated successfully!")
            
    return redirect('core:manager_dashboard', club_id=club.id)