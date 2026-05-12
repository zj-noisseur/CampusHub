import json
import logging
from datetime import timedelta

from django.conf import settings
from django.db.models import Max, Count, Q, F
from django.http import JsonResponse
from django.shortcuts import render
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import user_passes_test

from core.models import Institution, Club, ClubScrapeStatus
from core.services.tasks import orchestrator, orchestrator_retry_post

logger = logging.getLogger(__name__)

def is_superuser(user):
    return user.is_authenticated and user.is_superuser

@user_passes_test(is_superuser)
def admin_dashboard_home(request):
    selected_institution = request.GET.get("institution")
    selected_clubs = request.GET.getlist("club") or request.GET.getlist("club_ids")
    search_query = request.GET.get("search", "")
    date_sort = request.GET.get("sort", "newest")
    
    universities = Institution.objects.order_by("university_name")
    
    clubs = Club.objects.select_related("institution").annotate(
        latest_post_timestamp=Max("posts__timestamp"),
        post_count=Count("posts")
    )
    
    # Filter logic
    clean_club_ids = [cid for cid in selected_clubs if str(cid).isdigit()]
    if clean_club_ids:
        clubs = clubs.filter(id__in=clean_club_ids)
    elif selected_institution:
        clubs = clubs.filter(institution_id=selected_institution)
    
    if search_query:
        clubs = clubs.filter(
            Q(name__icontains=search_query) | 
            Q(ig_handle__icontains=search_query)
        )
        
    # Apply Sorting
    if date_sort == 'oldest':
        clubs = clubs.order_by(F('last_fetched_date').asc(nulls_last=True))
    else:
        clubs = clubs.order_by(F('last_fetched_date').desc(nulls_last=True))

    # For the search dropdown - smart grouping and naming
    all_clubs_qs = Club.objects.select_related('institution').all().order_by('institution__university_name', 'name')
    
    name_counts = {}
    for c in all_clubs_qs:
        name_counts[c.name] = name_counts.get(c.name, 0) + 1
    
    grouped_clubs = {}
    for c in all_clubs_qs:
        inst_name = c.institution.university_name
        if inst_name not in grouped_clubs:
            grouped_clubs[inst_name] = []
        
        display_name = f"{c.name} ({inst_name})" if name_counts[c.name] > 1 else c.name
        grouped_clubs[inst_name].append({
            'id': c.id,
            'name': display_name,
            'search_key': f"{c.name} {inst_name}".lower()
        })
    
    context = {
        'clubs': clubs,
        'grouped_clubs': grouped_clubs,
        'universities': universities,
        'selected_institution': int(selected_institution) if selected_institution else None,
        'selected_clubs': [int(c) for c in selected_clubs if str(c).isdigit()],
        'search_query': search_query,
        'date_sort': date_sort,
    }

    return render(request, 'admin_dashboard.html', context)

@user_passes_test(is_superuser)
def admin_dashboard_task_queue(request):
    statuses = ClubScrapeStatus.objects.all().select_related('club').order_by('-last_updated_at')

    tasks_data = []

    for status in statuses:
        tasks_data.append({
            'task_id': status.task_id,
            'task_name': status.latest_task_name,
            'display_name': status.latest_task_name.split('.')[-1] if status.latest_task_name else 'Task',
            'club_id': str(status.club.id) if status.club else None,
            'club_name': status.club.name if status.club else 'Unknown Club',
            'club_group': status.club.name if status.club else 'Unknown Club',
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

    tasks_data.sort(
        key=lambda task: -((task.get('date_done') or task.get('date_created')).timestamp()) if (task.get('date_done') or task.get('date_created')) else 0
    )
    
    has_recent_activity = False
    if statuses:
        latest_update = statuses[0].last_updated_at
        if latest_update and timezone.now() - latest_update < timedelta(seconds=30):
            has_recent_activity = True

    return render(request, 'admin_dashboard_tasks_fragment.html', {
        'tasks': tasks_data,
        'has_recent_activity': has_recent_activity,
        'history_task_count': len(tasks_data),
    })

@user_passes_test(is_superuser)
def admin_dashboard_task_status(request):
    task_id = request.GET.get('task_id')
    club_id = request.GET.get('club_id')
    
    scrape_status = None
    if task_id:
        scrape_status = ClubScrapeStatus.objects.filter(task_id=task_id).select_related('club').first()
    if not scrape_status and club_id:
        scrape_status = ClubScrapeStatus.objects.filter(club_id=club_id).select_related('club').first()
        
    if not scrape_status:
        return JsonResponse({'error': 'Status not found'}, status=404)

    return JsonResponse({
        'task_id': scrape_status.task_id,
        'state': scrape_status.state,
        'status': scrape_status.status,
        'progress': 100 if scrape_status.state == 'SUCCESS' else 0,
        'eta': None,
        'elapsed': (scrape_status.finished_at - scrape_status.started_at).total_seconds() if scrape_status.finished_at and scrape_status.started_at else ((scrape_status.last_updated_at - scrape_status.started_at).total_seconds() if scrape_status.last_updated_at and scrape_status.started_at else None),
        'current_item': scrape_status.current_item,
        'total_items': scrape_status.total_items,
        'current_image': scrape_status.current_image,
        'total_images': scrape_status.total_images,
        'phase': scrape_status.phase,
        'club_id': str(scrape_status.club_id),
        'failed_items': scrape_status.failed_items,
        'date_created': scrape_status.started_at.isoformat() if scrape_status.started_at else None,
        'date_done': scrape_status.finished_at.isoformat() if scrape_status.finished_at else None,
    })

@csrf_exempt
@require_POST
@user_passes_test(is_superuser)
def admin_dashboard_action(request):
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
        export_dir = str(settings.JSON_EXPORT_DIR)
        task_id = orchestrator(str(club.id), export_dir=export_dir)
        return JsonResponse({
            'ok': True,
            'action': action,
            'club_id': str(club.id),
            'ig_handle': club.ig_handle,
            'task_id': task_id,
            'status': 'queued',
        })

    if action == 'retry_failed_post':
        post_url = payload.get('post_url')
        if not post_url:
            return JsonResponse({'error': 'post_url is required for retrying'}, status=400)
            
        task_id = orchestrator_retry_post(str(club.id), post_url)
        return JsonResponse({
            'ok': True,
            'action': action,
            'club_id': str(club.id),
            'post_url': post_url,
            'task_id': task_id,
            'status': 'queued',
        })

    return JsonResponse({'error': 'Unknown action'}, status=400)
