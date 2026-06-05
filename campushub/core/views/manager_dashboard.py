from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from core.models import Club, Membership
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
    
    return render(request, 'manager_dashboard.html', context)

@login_required
def process_membership(request, membership_id, action):
    # 1. Grab the specific membership request
    membership = get_object_or_404(Membership, id=membership_id)
    
    # 2. Security Check: Is the person clicking this actually the manager?
    if not membership.club.managers.filter(user=request.user).exists():
        messages.error(request, 'You do not have permission to manage this club.')
        return redirect('core:manager_dashboard', club_id=membership.club.id)
        
    # 3. Process the action
    if action == 'approve':
        membership.status = 'APPROVED'
        
        today = date.today()
        policy = membership.club.renewal_policy
        if policy == 'ROLLING':
            membership.expired_at = timezone.now() + timezone.timedelta(days=365)
        elif policy == 'CALENDAR':
            membership.expired_at = timezone.make_aware(timezone.datetime(today.year, 12, 31, 23, 59, 59))
        elif policy == 'LIFETIME':
            membership.expired_at = None
            
        membership.save()
        messages.success(request, f'Approved {membership.user.student_name}!')
    elif action == 'reject':
        membership.status = 'REJECTED'
        membership.save()
        messages.success(request, 'Membership request rejected.')
        
    return redirect('core:manager_dashboard', club_id=membership.club.id)


@login_required
def extend_club_validity(request, club_id):
    club = get_object_or_404(Club, id=club_id)

    if not club.managers.filter(user=request.user, role='ROOT', is_active=True).exists():
        messages.error(request, 'You do not have permission to extend this club.')
        return redirect('core:manager_dashboard', club_id=club.id)

    if request.method == 'POST':
        club.extend_validity()
        messages.success(request, f'{club.name} validity extended to {club.valid_till.strftime("%b %d, %Y")}')

    return redirect('core:manager_dashboard', club_id=club.id)
