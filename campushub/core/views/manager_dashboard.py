from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from core.models import Club, Membership, Post, User
from datetime import date
from django.utils import timezone
from django.contrib.auth.hashers import make_password
import csv
import io
import random
import string

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

    all_official_members = memberships.filter(status__in=['APPROVED', 'Member'])
    active_members = all_official_members.filter(user__is_active=True)
    ghost_members = all_official_members.filter(user__is_active=False)
    pending_members = memberships.filter(status='PENDING')
    
    # Get all post lists for 3-step caption processing
    all_club_posts = Post.objects.filter(club=my_club).order_by('-timestamp')
    temporal_posts = all_club_posts
    event_type_posts = all_club_posts.filter(is_event=True)
    extraction_posts = all_club_posts.filter(is_event=True).select_related('event')
    
    from core.models import ClubScrapeStatus
    from datetime import timedelta
    
    status = ClubScrapeStatus.objects.filter(club=my_club).first()
    tasks_data = []
    if status:
        tasks_data.append({
            'task_id': status.task_id,
            'task_name': status.latest_task_name,
            'display_name': status.latest_task_name.split('.')[-1] if status.latest_task_name else 'Task',
            'club_id': str(status.club.id) if status.club else None,
            'club_name': status.club.name if status.club else 'Unknown Club',
            'is_scrape_task': True,
            'phase': status.phase,
            'progress': 100 if status.state == 'SUCCESS' else 0,
            'current_item': status.current_item,
            'total_items': status.total_items,
            'current_image': status.current_image,
            'total_images': status.total_images,
            'status': status.state or 'PENDING',
            'status_text': status.status,
            'eta': None,
            'elapsed': (status.finished_at - status.started_at).total_seconds() if status.finished_at and status.started_at else ((status.last_updated_at - status.started_at).total_seconds() if status.last_updated_at and status.started_at else None),
            'state': status.state or 'PENDING',
            'date_done': status.finished_at,
            'date_created': status.started_at,
            'date_group': (status.finished_at or status.started_at).date() if (status.finished_at or status.started_at) else None,
            'summary': status.extra,
            'failed_items': status.failed_items,
        })
        
    has_recent_activity = False
    if status and status.last_updated_at and timezone.now() - status.last_updated_at < timedelta(seconds=30):
        has_recent_activity = True
        
    context = {
        'club': my_club,
        'active_members': active_members,
        'ghost_members': ghost_members,
        'pending_members': pending_members,
        'total_members': all_official_members.count(),
        'pending_requests': pending_members.count(),
        'event_posts': extraction_posts,
        'temporal_posts': temporal_posts,
        'event_type_posts': event_type_posts,
        'extraction_posts': extraction_posts,
        'tasks': tasks_data,
        'has_recent_activity': has_recent_activity,
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
        if not club.can_extend:
            messages.warning(request, f'Club validity cannot be extended yet — {club.days_remaining} days still remaining (must be 30 or fewer).')
            return redirect('core:manager_dashboard', club_id=club.id)
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
        
        if post.event:
            event = post.event
            from core.views.event_detail import parse_date
            new_date = parse_date(date_val)
            if new_date:
                event.event_date = new_date
            event.location = venue_val
            event.save()
            
        messages.success(request, 'Event details successfully updated!')
        
    referer = request.META.get('HTTP_REFERER')
    if referer:
        return redirect(referer)
    return redirect('core:manager_dashboard', club_id=club.id)

def import_members(request, club_id):
    club = get_object_or_404(Club, id=club_id)
    
    if request.method == 'POST':
        csv_file = request.FILES.get('csv_file')
        
        # 1. THE BOUNCER: Make sure it's actually a CSV!
        if not csv_file or not csv_file.name.endswith('.csv'):
            messages.error(request, "Oops! Please make sure you uploaded a .csv file.")
            return redirect('core:manager_dashboard', club_id=club.id)
            
        # 2. Crack open the file in memory
        data_set = csv_file.read().decode('UTF-8')
        io_string = io.StringIO(data_set)
        
        # Skip the header row (StudentID, FullName, PhoneNumber, Faculty, Email)
        next(io_string, None) 
        
        success_count = 0
        ghost_count = 0
        
        # 3. Loop through the rows
        for row in csv.reader(io_string, delimiter=',', quotechar='"'):
            if len(row) < 2:
                continue # Skip empty or broken rows
                
            student_id_csv = row[0].strip()
            full_name_csv = row[1].strip()

            email_csv = row[4].strip() if len(row) > 4 else ""
            if not email_csv:
                email_csv = f"{student_id_csv}@pending.campushub.local"
            
            # Check if user exists. If not, create the Ghost Profile!
            user, created = User.objects.get_or_create(
                student_id=student_id_csv,
                defaults={
                    'student_name': full_name_csv,
                    'email': email_csv,
                    'is_active': False, # So they can't log in yet!
                }
            )
            
            if created:
                # Give the ghost a random, unguessable password
                random_pass = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
                user.password = make_password(random_pass)
                user.save()
                ghost_count += 1
                
            # 4. Add them to the club (whether real or ghost)
            Membership.objects.get_or_create(
                user=user,
                club=club,
                defaults={'status': 'APPROVED'}
            )
            success_count += 1
            
        messages.success(request, f"Import complete! Added {success_count} members ({ghost_count} are pending registration).")
        return redirect('core:manager_dashboard', club_id=club.id)

    # If it's a GET request, just show the upload form page
    return render(request, 'import_members.html', {'club': club})


from django.http import HttpResponse

@login_required
def club_extract_post_details(request, club_id, post_id):
    club = get_object_or_404(Club, id=club_id)
    
    is_manager = club.managers.filter(user=request.user, is_active=True).exists()
    if not is_manager:
        return HttpResponse("Unauthorized", status=403)
        
    post = get_object_or_404(Post, id=post_id, club=club)
    
    if not post.is_event:
        return HttpResponse("Post is not classified as an event.", status=400)
        
    from core.services.post_extraction import extract_details as run_extract
    post.extracted_details = run_extract(post.caption)
    post.save(update_fields=['extracted_details'])
    
    if post.event:
        event = post.event
        from core.views.event_detail import parse_date
        extracted_date = post.extracted_details.get('date')
        if extracted_date:
            new_date = parse_date(extracted_date)
            if new_date:
                event.event_date = new_date
        event.location = post.extracted_details.get('venue') or ""
        event.save()
        
    return render(request, 'club_data_extraction_row.html', {'post': post, 'club': club})


@login_required
def club_revert_post_extraction(request, club_id, post_id):
    club = get_object_or_404(Club, id=club_id)
    
    is_manager = club.managers.filter(user=request.user, is_active=True).exists()
    if not is_manager:
        return HttpResponse("Unauthorized", status=403)
        
    post = get_object_or_404(Post, id=post_id, club=club)
    post.extracted_details = {}
    post.save(update_fields=['extracted_details'])
    
    if post.event:
        event = post.event
        event.location = ""
        event.save()
        
    return render(request, 'club_data_extraction_row.html', {'post': post, 'club': club})


@login_required
def club_task_queue(request, club_id):
    club = get_object_or_404(Club, id=club_id)
    is_manager = club.managers.filter(user=request.user, is_active=True).exists()
    if not is_manager:
        return HttpResponse("Unauthorized", status=403)
        
    from core.models import ClubScrapeStatus
    from datetime import timedelta
    status = ClubScrapeStatus.objects.filter(club=club).first()
    tasks_data = []
    if status:
        tasks_data.append({
            'task_id': status.task_id,
            'task_name': status.latest_task_name,
            'display_name': status.latest_task_name.split('.')[-1] if status.latest_task_name else 'Task',
            'club_id': str(status.club.id) if status.club else None,
            'club_name': status.club.name if status.club else 'Unknown Club',
            'is_scrape_task': True,
            'phase': status.phase,
            'progress': 100 if status.state == 'SUCCESS' else 0,
            'current_item': status.current_item,
            'total_items': status.total_items,
            'current_image': status.current_image,
            'total_images': status.total_images,
            'status': status.state or 'PENDING',
            'status_text': status.status,
            'eta': None,
            'elapsed': (status.finished_at - status.started_at).total_seconds() if status.finished_at and status.started_at else ((status.last_updated_at - status.started_at).total_seconds() if status.last_updated_at and status.started_at else None),
            'state': status.state or 'PENDING',
            'date_done': status.finished_at,
            'date_created': status.started_at,
            'date_group': (status.finished_at or status.started_at).date() if (status.finished_at or status.started_at) else None,
            'summary': status.extra,
            'failed_items': status.failed_items,
        })
        
    has_recent_activity = False
    if status and status.last_updated_at and timezone.now() - status.last_updated_at < timedelta(seconds=30):
        has_recent_activity = True
        
    return render(request, 'club_dashboard_tasks_fragment.html', {
        'tasks': tasks_data,
        'has_recent_activity': has_recent_activity,
        'history_task_count': len(tasks_data),
        'club': club,
    })


@login_required
def club_classify_post_temporal(request, club_id, post_id):
    club = get_object_or_404(Club, id=club_id)
    
    # Check if the user is a manager
    is_manager = club.managers.filter(user=request.user, is_active=True).exists()
    if not is_manager:
        return HttpResponse("Unauthorized", status=403)
        
    post = get_object_or_404(Post, id=post_id, club=club)
    
    if request.method == 'POST':
        from core.services.post_categorization import assign_event_status_to_post
        assign_event_status_to_post(post)
        return render(request, 'club_temporal_classification_row.html', {'post': post, 'club': club})
    return HttpResponse('Invalid request', status=400)


@login_required
def club_update_post_event_status(request, club_id, post_id):
    club = get_object_or_404(Club, id=club_id)
    
    # Check if the user is a manager
    is_manager = club.managers.filter(user=request.user, is_active=True).exists()
    if not is_manager:
        return HttpResponse("Unauthorized", status=403)
        
    post = get_object_or_404(Post, id=post_id, club=club)
    
    if request.method == 'POST':
        val = request.POST.get('is_event') or request.GET.get('is_event')
        if val == 'True':
            post.is_event = True
        elif val == 'False':
            post.is_event = False
        elif val == 'None':
            post.is_event = None
        post.save(update_fields=['is_event'])
        return render(request, 'club_temporal_classification_row.html', {'post': post, 'club': club})
    return HttpResponse('Invalid request', status=400)


@login_required
def club_classify_post_event(request, club_id, post_id):
    club = get_object_or_404(Club, id=club_id)
    
    # Check if the user is a manager
    is_manager = club.managers.filter(user=request.user, is_active=True).exists()
    if not is_manager:
        return HttpResponse("Unauthorized", status=403)
        
    post = get_object_or_404(Post, id=post_id, club=club)
    
    if request.method == 'POST':
        from core.services.post_categorization import assign_category_to_post
        assign_category_to_post(post)
        return render(request, 'club_event_classification_row.html', {'post': post, 'club': club})
    return HttpResponse('Invalid request', status=400)


@login_required
def club_update_post_event_category(request, club_id, post_id):
    club = get_object_or_404(Club, id=club_id)
    
    # Check if the user is a manager
    is_manager = club.managers.filter(user=request.user, is_active=True).exists()
    if not is_manager:
        return HttpResponse("Unauthorized", status=403)
        
    post = get_object_or_404(Post, id=post_id, club=club)
    
    if request.method == 'POST':
        category_val = request.POST.get('category') or request.GET.get('category')
        valid_keys = [k for k, v in Post.CATEGORY_CHOICES]
        if category_val in valid_keys:
            post.category = category_val
            post.save(update_fields=['category'])
        return render(request, 'club_event_classification_row.html', {'post': post, 'club': club})
    return HttpResponse('Invalid request', status=400)



