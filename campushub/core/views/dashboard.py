from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from ..models import Club, Membership
from django.shortcuts import get_object_or_404

@login_required
def manager_dashboard(request):
    # Fetch the club(s) this specific user manages. 
    # (Note: Change 'manager' below to whatever field name you used in your Club model to link the owner!)
    managed_clubs = Club.objects.filter(managers__user=request.user)
    
    if not managed_clubs.exists():
        messages.error(request, 'You do not have permission to view the manager dashboard.')
        return redirect('profile')
        
    # For now, let's assume they manage one club and grab the first one
    my_club = managed_clubs.first()
    
    # Get all the students who have applied or joined this club
    memberships = Membership.objects.filter(club=my_club)
    
    context = {
        'club': my_club,
        'memberships': memberships,
        # Let's count them for some cool stats on the dashboard
        'total_members': memberships.filter(status='approved').count(),
        'pending_requests': memberships.filter(status='pending').count(),
    }
    
    return render(request, 'core/dashboard.html', context)

@login_required
def process_membership(request, membership_id, action):
    # 1. Grab the specific membership request
    membership = get_object_or_404(Membership, id=membership_id)
    
    # 2. Security Check: Is the person clicking this actually the manager of THIS club?
    if membership.club.manager != request.user:
        messages.error(request, 'You do not have permission to manage this club.')
        return redirect('manager_dashboard')
        
    # 3. Process the action
    if action == 'approve':
        membership.is_approved = True
        membership.save()
        messages.success(request, f'Approved {membership.user.student_name}!')
    elif action == 'reject':
        membership.delete() # Or you could add an 'is_rejected' field if you want to keep the record
        messages.success(request, 'Membership request rejected.')
        
    # 4. Refresh the dashboard
    return redirect('manager_dashboard')