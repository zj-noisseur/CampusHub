from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required

from core.models import Club, Event, PreRegisteredAttendee, Attendance, ClubManager
from django.utils import timezone
from django.db.models import Q

@login_required
def club_admin_dashboard(request, club_id, event_id=None):
    club = get_object_or_404(Club, id=club_id)
    
    if not event_id:
        latest_event = Event.objects.filter(club=club).order_by('-event_date').first()
        if latest_event:
            return redirect('core:event_admin_dashboard', club_id=club.id, event_id=latest_event.id)
        else:
            # If no events exist at all, we still render the page but events will be empty
            events = []
    else:
        events = Event.objects.filter(club=club, id=event_id)
    
    return render(request, 'event_manage.html', {
        'club': club,
        'events': events,
    })

@login_required
def toggle_ready_status(request, event_id, prereg_id):
    prereg = get_object_or_404(PreRegisteredAttendee, id=prereg_id, event_id=event_id)
    
    prereg.is_ready = not prereg.is_ready
    prereg.save()
    
    return redirect('core:event_admin_dashboard', club_id=prereg.event.club.id, event_id=prereg.event.id)

@login_required
def toggle_attended_status(request, event_id, prereg_id):
    prereg = get_object_or_404(PreRegisteredAttendee, id=prereg_id, event_id=event_id)
    
    # We check if an Attendance record already exists to decide whether to create or delete it.
    # The PreRegisteredAttendee.is_attended status will be updated via Django signals.
    
    if prereg.user:
        attendance = Attendance.objects.filter(event=prereg.event, user=prereg.user)
    else:
        attendance = Attendance.objects.filter(event=prereg.event, guest_email=prereg.guest_email)

    if attendance.exists():
        attendance.delete()
    else:
        if prereg.user:
            Attendance.objects.create(event=prereg.event, user=prereg.user)
        else:
            Attendance.objects.create(
                event=prereg.event, 
                guest_email=prereg.guest_email,
                guest_name=prereg.guest_name
            )
            
    return redirect('core:event_admin_dashboard', club_id=prereg.event.club.id, event_id=prereg.event.id)


@login_required
def my_events(request):
    user = request.user
    
    my_registrations = PreRegisteredAttendee.objects.filter(
        Q(user=user) | Q(guest_email=user.email)
    ).select_related('event', 'event__club').distinct().order_by('-event__event_date')
    
    upcoming_events = []
    ongoing_events = []
    pending_events = []
    past_events = []
    
    today = timezone.localdate()
    
    for prereg in my_registrations:
        if prereg.event.status == 'FINISHED':
            past_events.append(prereg)
        elif prereg.event.status == 'ONGOING':
            ongoing_events.append(prereg)
        elif prereg.event.status == 'PREPARING':
            upcoming_events.append(prereg)
        else:
            if prereg.event.event_date < today:
                past_events.append(prereg)
            else:
                upcoming_events.append(prereg)
            
    attended_count = sum(1 for prereg in my_registrations if prereg.is_attended)
    
    context = {
        'user': user,
        'upcoming_events': upcoming_events,
        'ongoing_events': ongoing_events,
        'pending_events': pending_events,
        'past_events': past_events,
        'joined_count': my_registrations.count(),
        'attended_count': attended_count,
        'today': today,
    }
    
    return render(request, 'my_events.html', context)


@login_required
def student_dashboard(request):
    user = request.user
    
    # 1. Get events this user actually attended
    # Use Q to include events where the user is identified by their account OR guest email
    participated_events = Event.objects.filter(
        Q(attendances__user=user) | Q(attendances__guest_email=user.email)
    ).distinct().order_by('-event_date')
    
    # 2. Get all registrations (RSVPs) for this user (account or guest email)
    my_registrations = PreRegisteredAttendee.objects.filter(
        Q(user=user) | Q(guest_email=user.email)
    ).distinct().order_by('-event__event_date')
    
    # 3. Get clubs (Looking THROUGH the ClubManager and Membership tables)
    managed_clubs = Club.objects.filter(managers__user=user)
    joined_clubs = Club.objects.filter(members__user=user).exclude(managers__user=user)
    
    context = {
        'user': user,
        'participated_events': participated_events,
        'my_registrations': my_registrations, 
        'managed_clubs': managed_clubs,
        'joined_clubs': joined_clubs,
        'today': timezone.localdate(),
    }
    
    return render(request, 'student_dashboard.html', context)


@login_required
def set_event_status(request, event_id, status):
    event = get_object_or_404(Event, id=event_id)
    
    if status.upper() in dict(Event.STATUS_CHOICES):
        event.status = status.upper()
        event.save()
    
    return redirect('core:event_admin_dashboard', club_id=event.club.id, event_id=event.id)

def club_profile(request, club_id):
    # Optimize club queries by selecting/prefetching relationships
    club = get_object_or_404(
        Club.objects.select_related('institution')
        .prefetch_related('managers__user', 'members__user'),
        id=club_id
    )
    
    # 1. Fetch and prefetch events (with their linked post and post's images)
    events = (
        Event.objects.filter(club=club)
        .select_related('post')
        .prefetch_related('post__postimage_set')
        .order_by('event_date')
    )
    
    # 2. Fetch and prefetch club posts (Instagram posts/feed updates), capped for speed
    from ..models import Post
    club_posts = (
        Post.objects.filter(club=club)
        .prefetch_related('postimage_set')
        .order_by('-timestamp')[:48]
    )

    from django.db.models import Q
    scraped_events = (
        Post.objects.filter(club=club, events__isnull=True)
        .filter(Q(is_event=True) | ~Q(category='MISC'))
        .prefetch_related('postimage_set')
        .order_by('-timestamp')[:120]
    )
    
    approved_members = [m for m in club.members.all() if m.status in ['ACTIVE', 'APPROVED']]

    # Check if the logged-in user is in the managers
    is_manager = False
    user_membership = None
    
    if request.user.is_authenticated:
        # Looking through the pre-fetched managers
        is_manager = any(m.user == request.user and m.is_active for m in club.managers.all())
        user_membership = next((m for m in club.members.all() if m.user == request.user), None)
        
    attended_event_ids = []
    if request.user.is_authenticated:
        attended_event_ids = list(Attendance.objects.filter(
            event__club=club,
            user=request.user
        ).values_list('event_id', flat=True))

    is_member_active = False
    if request.user.is_authenticated:
        is_member_active = any(m.user == request.user and m.status in ['ACTIVE', 'APPROVED'] for m in club.members.all())

    # Compute total events count
    from django.db.models import Q
    manual_events_count = events.count()
    scraped_events_count = Post.objects.filter(
        club=club,
        events__isnull=True
    ).filter(
        Q(is_event=True) | ~Q(category='MISC')
    ).count()
    total_events_count = manual_events_count + scraped_events_count
    total_feed_count = club_posts.count()

    context = {
        'club': club,
        'events': events,
        'club_posts': club_posts,
        'scraped_events': scraped_events,
        'is_manager': is_manager,
        'is_member': is_member_active,
        'attended_event_ids': attended_event_ids,
        'user_membership': user_membership,
        'total_events_count': total_events_count,
        'total_feed_count': total_feed_count,
        'approved_members': approved_members,
    }
    return render(request, 'club_profile.html', context)

@login_required
def club_settings(request, club_id):
    club = get_object_or_404(Club, id=club_id)
    
    # Check if the user is a manager
    is_manager = club.managers.filter(user=request.user, is_active=True).exists()
    if not is_manager:
        return redirect('core:club_profile', club_id=club.id)
        
    from ..forms import ClubSettingsForm
    
    if request.method == 'POST':
        form = ClubSettingsForm(request.POST, request.FILES, instance=club)
        if form.is_valid():
            form.save()
            return redirect('core:club_profile', club_id=club.id)
    else:
        form = ClubSettingsForm(instance=club)
        
    context = {
        'club': club,
        'form': form,
    }
    return render(request, 'club_settings.html', context)
    
@login_required
def create_event(request, club_id):
    club = get_object_or_404(Club, id=club_id)
    
    # Check if the user is a manager for the club
    if not club.managers.filter(user=request.user, is_active=True).exists():
        return redirect('core:club_profile', club_id=club.id)
    
    from ..forms import EventCreationForm
    from ..models import Post
    
    if request.method == 'POST':
        form = EventCreationForm(request.POST, request.FILES)
        if form.is_valid():
            event = form.save(commit=False)
            event.club = club
            
            # Since Event requires a Post (OneToOne), we create a mock Post record 
            # to bypass the Instagram scraper requirement for manual events.
            desc = form.cleaned_data.get('description') or f"Manually created event: {event.title}"
            category = form.cleaned_data.get('category') or 'WORKSHOP'
            mock_post = Post.objects.create(
                club=club,
                short_code=f"manual_{timezone.now().timestamp()}",
                caption=desc,
                category=category,
                timestamp=timezone.now()
            )
            event.post = mock_post
            event.save()
            
            banner_image = form.cleaned_data.get('banner_image')
            if banner_image:
                from ..models import PostImage
                PostImage.objects.create(
                    post=mock_post,
                    image=banner_image,
                    order=1
                )
            return redirect('core:event_admin_dashboard', club_id=club.id, event_id=event.id)
    else:
        form = EventCreationForm()
        
    return render(request, 'create_event.html', {
        'club': club,
        'form': form,
    })


@login_required
def edit_event(request, club_id, event_id):
    club = get_object_or_404(Club, id=club_id)
    event = get_object_or_404(Event, id=event_id, club=club)
    
    # Check if the user is a manager for the club
    if not club.managers.filter(user=request.user, is_active=True).exists():
        return redirect('core:club_profile', club_id=club.id)
        
    from ..forms import EventCreationForm
    from ..models import PostImage
    
    if request.method == 'POST':
        form = EventCreationForm(request.POST, request.FILES, instance=event)
        if form.is_valid():
            event = form.save()
            
            # Update the linked post's caption and category
            desc = form.cleaned_data.get('description')
            category = form.cleaned_data.get('category')
            if desc:
                event.post.caption = desc
            if category:
                event.post.category = category
            event.post.save()
                
            # Update or create the banner image
            banner_image = form.cleaned_data.get('banner_image')
            if banner_image:
                PostImage.objects.filter(post=event.post).delete()
                PostImage.objects.create(
                    post=event.post,
                    image=banner_image,
                    order=1
                )
            return redirect('core:event_admin_dashboard', club_id=club.id, event_id=event.id)
    else:
        # Load the post's caption as the description initial value and category
        initial_data = {
            'description': event.post.caption,
            'category': event.post.category
        }
        form = EventCreationForm(instance=event, initial=initial_data)
        
    return render(request, 'create_event.html', {
        'club': club,
        'event': event,
        'form': form,
        'is_edit': True,
    })
