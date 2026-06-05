from django.shortcuts import render, get_object_or_404, redirect
from core.models import Event, Post
from django.contrib.auth.decorators import login_required
from django.utils import timezone

def event_detail(request, event_id=None, post_id=None):
    if not request.user.is_authenticated:
        if request.headers.get('HX-Request'):
            return render(request, 'event_detail_auth_required.html')
        return redirect('core:login')

    if post_id:
        post = get_object_or_404(Post, id=post_id)
        if hasattr(post, 'events'):
            event = post.events
        else:
            # Auto-create dummy Event for scraped post
            title = post.caption[:50] + "..." if len(post.caption) > 50 else (post.caption or "Imported Event")
            if not title.strip():
                title = "Imported Event"
            event = Event.objects.create(
                club=post.club,
                post=post,
                title=title,
                event_date=post.timestamp.date(),
                location="TBA",
                fee=0.00,
                requires_approval=True
            )
    else:
        event = get_object_or_404(Event, id=event_id)
        
    attendance_count = event.attendances.count()
    
    template_name = 'event_detail_partial.html' if request.headers.get('HX-Request') else 'event_detail.html'
    
    return render(request, template_name, {
        'event': event,
        'attendance_count': attendance_count,
    })
