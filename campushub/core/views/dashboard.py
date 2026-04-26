import json
import os

from celery.result import AsyncResult
from django.db.models import Max
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.db.models import Count

from django_celery_results.models import TaskResult
from core.models import Institution, Club
from core.task import run_club_scrape_task

def dashboard_home(request):
    selected_institution = request.GET.get("institution")
    universities = Institution.objects.order_by("university_name")
    clubs = Club.objects.select_related(
        "institution"
    ).annotate( # this is a derived field that does not write to the database nor is it part of the model
        latest_post_timestamp=Max("posts__timestamp"),
        # to avoid collision with the related name, ie "posts", use the singular noun instead
        post_count  = Count("posts")
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

def dashboard_task_queue(request):
    # Fetch tasks that are queued, running, successful, or failed.
    # We order by creation/done time so the newest tasks appear first.
    task_results = TaskResult.objects.filter(
        status__in=['PENDING', 'PROGRESS', 'SUCCESS', 'FAILURE']
    ).order_by('-date_done', '-date_created')

    tasks_data = []
    active_task_count = task_results.filter(status='PROGRESS').count()

    for task in task_results:
        try:
            meta = json.loads(task.meta) if task.meta else {}
        except (json.JSONDecodeError, TypeError):
            meta = {}


        result_data = task.result
        if isinstance(result_data, str):
            try:
                result_data = json.loads(result_data)
            except json.JSONDecodeError:
                result_data = None

        if isinstance(result_data, dict):
            club_id = result_data.get('club_id')
            from core.models import Club
            club = Club.objects.filter(id=club_id).only('name').first()
            if club:
                club_name = club.name

        if not club_id and task.task_args:
            try:
                task_args = json.loads(task.task_args)
                if isinstance(task_args, (list, tuple)) and task_args:
                    club_id = task_args[0]
            except (json.JSONDecodeError, TypeError):
                pass

        if not club_id and task.task_kwargs:
            try:
                task_kwargs = json.loads(task.task_kwargs)
                club_id = task_kwargs.get('club_id') or task_kwargs.get('club_id')
            except (json.JSONDecodeError, TypeError):
                pass
        
        if club_id and not club_name:
            from core.models import Club
            club = Club.objects.filter(id=club_id).only('name').first()
            if club:
                club_name = club.name

        if not club_name:
            club_name = 'Unknown Club'

        label = task.status
        if task.status == 'PENDING':
            label = 'Queued'
        elif task.status == 'PROGRESS':
            label = meta.get('status', 'Running...')
        elif task.status == 'SUCCESS':
            label = meta.get('status', 'Completed')
        elif task.status == 'FAILURE':
            label = meta.get('status', 'Failed')
            club_name = 'N/A'

        tasks_data.append({
            'task_id': task.task_id,
            'club_id': club_id,
            'club_name': club_name,
            'progress': meta.get('progress', 100 if task.status == 'SUCCESS' else 0),
            'status': label,
            'eta': meta.get('eta'),
            'elapsed': meta.get('elapsed'),
            'state': task.status,
            'date_done': task.date_done,
        })

    return render(request, 'dashboard_tasks_fragment.html', {
        'tasks': tasks_data,
        'active_task_count': active_task_count,
        'history_task_count': len(tasks_data),
    })

def dashboard_task_status(request):
    task_id = request.GET.get('task_id')
    if not task_id:
        return JsonResponse({'error': 'task_id is required'}, status=400)

    result = AsyncResult(task_id)
    info = result.info or {}

    return JsonResponse({
        'task_id': task_id,
        'state': result.state,
        'status': info.get('status'),
        'progress': info.get('progress'),
        'eta': info.get('eta'),
        'elapsed': info.get('elapsed'),
    })

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
        result = run_club_scrape_task.delay(str(club.id), export_dir=export_dir)
        return JsonResponse({
            'ok': True,
            'action': action,
            'club_id': str(club.id),
            'ig_handle': club.ig_handle,
            'task_id': result.id,
            'status': 'queued',
            'items_returned': None,
            'created_count': None,
            'export_dir': export_dir,
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
