import json
import os

from django.db.models import Max
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from core.models import Club, Institution
from core.task import run_club_scrape_task

def dashboard(request):
    selected_institution = request.GET.get("institution")
    universities = Institution.objects.order_by("university_name")
    clubs = Club.objects.select_related(
        "institution"
    ).annotate( # this is a derived field that does not write to the database nor is it part of the model
        latest_post_timestamp=Max("posts__timestamp")
    )
     

    # latest_post = Prefetch(
    #         "posts", 
    #         queryset=Post.objects.order_by("-timestamp")[:1],
    #         to_attr="latest_post"
    #     )

    # clubs = clubs.prefetch_related(latest_post)

    if selected_institution:
        clubs = clubs.filter(institution_id=selected_institution)

    return render(request, 'dashboard.html', {'clubs': clubs, "universities": universities, "selected_institution": selected_institution})

@csrf_exempt
@require_POST
def dashboard_action(request):
    try:
        payload = json.loads(request.body.decode('utf-8'))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse({'error': 'Invalid JSON payload'}, status=400)

    club_id = payload.get('club_id')
    action = payload.get('action')
    if not club_id or not action:
        return JsonResponse({'error': 'club_id and action are required'}, status=400)

    club = Club.objects.filter(id=club_id).only('id', 'ig_handle').first()
    if not club:
        return JsonResponse({'error': 'Club not found'}, status=404)

    if not club.ig_handle:
        return JsonResponse({'error': 'Club missing Instagram handle'}, status=400)

    if action == 'scrape_posts':
        export_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'export'))
        result = run_club_scrape_task(club, export_dir=export_dir)
        return JsonResponse({
            'ok': True,
            'action': action,
            'club_id': str(club.id),
            'ig_handle': club.ig_handle,
            'items_returned': result.get('items_returned'),
            'created_count': result.get('created_count'),
            'export_dir': result.get('export_dir'),
        })

    if action == 'update_profile_picture':
        return JsonResponse({
            'ok': True,
            'action': action,
            'club_id': str(club.id),
            'ig_handle': club.ig_handle,
            'message': 'Profile picture update action received',
        })

    return JsonResponse({'error': 'Unknown action'}, status=400)
