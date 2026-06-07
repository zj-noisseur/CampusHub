from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from core.models import Club, Membership, Post
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
    
    # Get event posts for metadata editing
    event_posts = Post.objects.filter(club=my_club, is_event=True).select_related('events').order_by('-timestamp')
    
    context = {
        'club': my_club,
        'approved_members': approved_members,
        'pending_members': pending_members,
        'total_members': approved_members.count(),
        'pending_requests': pending_members.count(),
        'event_posts': event_posts,
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


@login_required
def update_post_extracted_details(request, club_id, post_id):
    club = get_object_or_404(Club, id=club_id)
    
    if not club.managers.filter(user=request.user).exists():
        messages.error(request, 'You do not have permission to manage this club.')
        return redirect('core:profile')
        
    post = get_object_or_404(Post, id=post_id, club=club)
    
    if request.method == 'POST':
        date_val = request.POST.get('custom_date') or request.POST.get('date_choice')
        venue_val = request.POST.get('custom_venue') or request.POST.get('venue_choice')
        link_val = request.POST.get('custom_link') or request.POST.get('link_choice')
        
        date_val = (date_val or '').strip()
        venue_val = (venue_val or '').strip()
        link_val = (link_val or '').strip()
        
        details = post.extracted_details or {}
        details['date'] = date_val
        details['venue'] = venue_val
        details['link'] = link_val
        post.extracted_details = details
        post.save(update_fields=['extracted_details'])
        
        if hasattr(post, 'events'):
            event = post.events
            from core.views.event_detail import parse_date
            new_date = parse_date(date_val)
            if new_date:
                event.event_date = new_date
            event.location = venue_val
            event.save()
            
        messages.success(request, 'Event details successfully updated!')
        
    return redirect('core:manager_dashboard', club_id=club.id)
