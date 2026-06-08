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

        # No auto-created dummy Event for scraped posts; if an Event does not exist, we simply skip rendering.

    else:
        event = get_object_or_404(Event, id=event_id)
        post = event.post
        if post and not post.extracted_details and post.is_event:
            from core.services.post_extraction import extract_details as run_extract
            post.extracted_details = run_extract(post.caption)
            post.save(update_fields=['extracted_details'])
        
    attendance_count = event.attendances.count()
    user_prereg = event.pre_registered.filter(user=request.user).first() if request.user.is_authenticated else None
    
    template_name = 'event_detail_partial.html' if request.headers.get('HX-Request') else 'event_detail.html'
    
    return render(request, template_name, {
        'event': event,
        'attendance_count': attendance_count,
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
                attendance_count = event.attendances.count()
                user_prereg = event.pre_registered.filter(user=request.user).first()
                return render(request, 'event_detail_partial.html', {
                    'event': event,
                    'attendance_count': attendance_count,
                    'user_prereg': user_prereg,
                    'join_error': 'You must upload a payment receipt for this paid event.',
                })
            messages.error(request, 'You must upload a payment receipt for this paid event.')
            next_url = request.POST.get('next') or request.META.get('HTTP_REFERER') or f'/event/{event.id}/'
            return redirect(next_url)

        PreRegisteredAttendee.objects.create(
            event=event,
            user=request.user,
            status=status,
            receipt=receipt,
        )

    # After joining (or if already joined), return the updated partial for HTMX
    if is_htmx:
        attendance_count = event.attendances.count()
        user_prereg = event.pre_registered.filter(user=request.user).first()
        return render(request, 'event_detail_partial.html', {
            'event': event,
            'attendance_count': attendance_count,
            'user_prereg': user_prereg,
        })

    # Non-HTMX fallback: redirect back to referer
    next_url = request.POST.get('next') or request.META.get('HTTP_REFERER') or f'/event/{event.id}/'
    return redirect(next_url)
