import re
from dateutil import parser
from django.shortcuts import render, get_object_or_404, redirect
from core.models import Event, Post
from django.contrib.auth.decorators import login_required
from django.utils import timezone

def parse_date(date_str):
    if not date_str:
        return None
    try:
        # Strip ordinals (e.g. 14th -> 14)
        clean_str = re.sub(r'(\d+)(st|nd|rd|th)', r'\1', date_str)
        return parser.parse(clean_str).date()
    except Exception:
        return None

def parse_time(time_str):
    if not time_str:
        return None
    try:
        return parser.parse(time_str).time()
    except Exception:
        return None

def event_detail(request, event_id=None, post_id=None):
    if not request.user.is_authenticated:
        if request.headers.get('HX-Request'):
            return render(request, 'event_detail_auth_required.html')
        return redirect('core:login')

    if post_id:
        post = get_object_or_404(Post, id=post_id)
        
        # Populate extracted details if empty (only for upcoming events)
        if not post.extracted_details and post.is_event:
            from core.services.post_extraction import extract_details as run_extract
            post.extracted_details = run_extract(post.caption)
            post.save(update_fields=['extracted_details'])

        if not post.event:
            # Auto-create an event for scraped posts so users can RSVP
            from django.utils import timezone
            event = Event.objects.create(
                club=post.club,
                title=f"{post.club.name} Event",
                event_date=timezone.now()
            )
            # Link the post to the new event
            post.event = event
            post.is_primary_event_post = True
            post.save(update_fields=['event', 'is_primary_event_post'])
        else:
            event = post.event

    else:
        event = get_object_or_404(Event, id=event_id)
        post = event.primary_post
        if post and not post.extracted_details and post.is_event:
            from core.services.post_extraction import extract_details as run_extract
            post.extracted_details = run_extract(post.caption)
            post.save(update_fields=['extracted_details'])
        
    joined_attendees = event.pre_registered.filter(status='APPROVED').select_related('user')
    attendance_count = joined_attendees.count()
    recent_attendees = list(joined_attendees[:3])
    user_prereg = event.pre_registered.filter(user=request.user).first() if request.user.is_authenticated else None
    
    template_name = 'event_detail_partial.html' if request.headers.get('HX-Request') else 'event_detail.html'
    
    return render(request, template_name, {
        'event': event,
        'post': post,
        'attendance_count': attendance_count,
        'recent_attendees': recent_attendees,
        'user_prereg': user_prereg,
    })

from django.contrib import messages
from core.models import PreRegisteredAttendee

@login_required
def join_event(request, event_id):
    if request.method != 'POST':
        return redirect('core:feed')

    event = get_object_or_404(Event, id=event_id)
    is_htmx = request.headers.get('HX-Request') == 'true'

    # Check if already joined
    prereg = event.pre_registered.filter(user=request.user).first()
    if not prereg:
        status = 'PENDING'
        if event.join_mode == 'FREE':
            status = 'APPROVED'

        receipt = request.FILES.get('receipt')
        if event.join_mode == 'FEE' and not receipt:
            if is_htmx:
                # Re-render the partial with an error message
                joined_attendees = event.pre_registered.filter(status='APPROVED').select_related('user')
                attendance_count = joined_attendees.count()
                recent_attendees = list(joined_attendees[:3])
                user_prereg = event.pre_registered.filter(user=request.user).first()
                return render(request, 'event_detail_partial.html', {
                    'event': event,
                    'attendance_count': attendance_count,
                    'recent_attendees': recent_attendees,
                    'user_prereg': user_prereg,
                    'join_error': 'You must upload a payment receipt for this paid event.',
                })
            messages.error(request, 'You must upload a payment receipt for this paid event.')
            next_url = request.POST.get('next') or request.META.get('HTTP_REFERER') or f'/event/{event.id}/'
            return redirect(next_url)

        user = request.user
        is_ready = bool(user.student_id and user.email and user.student_name)

        PreRegisteredAttendee.objects.create(
            event=event,
            user=user,
            status=status,
            receipt=receipt,
            is_ready=is_ready,
        )

    # After joining (or if already joined), return the updated partial for HTMX
    if is_htmx:
        joined_attendees = event.pre_registered.filter(status='APPROVED').select_related('user')
        attendance_count = joined_attendees.count()
        recent_attendees = list(joined_attendees[:3])
        user_prereg = event.pre_registered.filter(user=request.user).first()
        return render(request, 'event_detail_partial.html', {
            'event': event,
            'attendance_count': attendance_count,
            'recent_attendees': recent_attendees,
            'user_prereg': user_prereg,
        })

    # Non-HTMX fallback: redirect back to referer
    next_url = request.POST.get('next') or request.META.get('HTTP_REFERER') or f'/event/{event.id}/'
    return redirect(next_url)
