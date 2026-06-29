import json
import secrets
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.core.signing import TimestampSigner, SignatureExpired, BadSignature
from core.models import Event, Attendance

@require_POST
def generate_qr_token(request, event_id):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Unauthorized'}, status=401)
        
    event = get_object_or_404(Event, id=event_id)
    
    # Check if user is a manager for this event's club
    if not event.club:
        return JsonResponse({'error': 'Event has no club'}, status=400)
        
    is_manager = event.club.managers.filter(user=request.user, is_active=True).exists()
    if not is_manager and not request.user.is_superuser:
        return JsonResponse({'error': 'Forbidden'}, status=403)
        
    try:
        data = json.loads(request.body)
        action = data.get('action', 'generate')
    except json.JSONDecodeError:
        action = 'generate'
        
    if action == 'clear':
        event.qr_token = None
        event.save(update_fields=['qr_token'])
        return JsonResponse({'status': 'cleared'})
    else:
        # Generate new token
        raw_token = secrets.token_urlsafe(32)
        event.qr_token = raw_token
        event.save(update_fields=['qr_token'])
        
        # Cryptographically sign the token with the current timestamp
        signer = TimestampSigner()
        signed_token = signer.sign(raw_token)
        
        return JsonResponse({'status': 'generated', 'token': signed_token})

def event_qr_checkin(request, event_id, token):
    event = get_object_or_404(Event, id=event_id)
    
    signer = TimestampSigner()
    try:
        # Verify the signature and ensure it is not older than 15 seconds
        raw_token = signer.unsign(token, max_age=15)
    except (SignatureExpired, BadSignature):
        return render(request, 'checkin_error.html', {'event': event})
    
    if not event.qr_token or event.qr_token != raw_token:
        # Invalid token (or it was manually cleared)
        return render(request, 'checkin_error.html', {'event': event})
        
    # At this point the token is valid. If the user is not logged in, redirect them to login first.
    if not request.user.is_authenticated:
        from django.contrib.auth.views import redirect_to_login
        from django.conf import settings
        return redirect_to_login(request.get_full_path(), login_url=settings.LOGIN_URL)
        
    # Valid token and logged in, mark attendance
    attendance, created = Attendance.objects.get_or_create(
        event=event,
        user=request.user,
        defaults={}
    )
    
    return render(request, 'checkin_success.html', {
        'event': event,
        'attendance': attendance,
        'created': created
    })
