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

        if hasattr(post, 'events'):
            event = post.events
        else:
            # Auto-create dummy Event for scraped post
            title = post.caption[:50] + "..." if len(post.caption) > 50 else (post.caption or "Imported Event")
            if not title.strip():
                title = "Imported Event"

            extracted = post.extracted_details or {}
            event_date = parse_date(extracted.get('date')) or post.timestamp.date()
            location = extracted.get('venue') or "TBA"

            start_time = None
            end_time = None
            time_val = extracted.get('time')
            if time_val:
                parts = re.split(r'[-–—to]', time_val)
                if len(parts) >= 1:
                    start_time = parse_time(parts[0].strip())
                if len(parts) >= 2:
                    end_time = parse_time(parts[1].strip())

            event = Event.objects.create(
                club=post.club,
                post=post,
                title=title,
                event_date=event_date,
                location=location,
                start_time=start_time,
                end_time=end_time,
                fee=0.00,
                requires_approval=True
            )
    else:
        event = get_object_or_404(Event, id=event_id)
        post = event.post
        if post and not post.extracted_details and post.is_event:
            from core.services.post_extraction import extract_details as run_extract
            post.extracted_details = run_extract(post.caption)
            post.save(update_fields=['extracted_details'])
        
    attendance_count = event.attendances.count()
    
    template_name = 'event_detail_partial.html' if request.headers.get('HX-Request') else 'event_detail.html'
    
    return render(request, template_name, {
        'event': event,
        'attendance_count': attendance_count,
    })
