# testing purposes only

# this is a simplified celery tasks file to reduce complexity and focus on the core workflow logic

# use this particular setup with a separate database for storing the celery resutls and different instance for the broker 

# DJANGO_CELERY_RESULTS_DB_ALIAS=test \
# CELERY_BROKER_URL=redis://localhost:6379/1 \
# celery -A campushub worker -Q testworker -l info

# DJANGO_CELERY_RESULTS_DB_ALIAS=test CELERY_BROKER_URL=redis://localhost:6379/1 celery -A campushub worker -Q testworker -l info
import json
import os
from datetime import datetime, timezone as dt_timezone

import requests
from django.conf import settings
from django.utils import timezone
from django.core.files.base import ContentFile

from celery import shared_task, chain, chord

from core.models import Club, Post, PostImage
from core.views.apify import fetch_instagram_posts_via_apify

def get_export_dir(export_dir=None):
    '''
    Export directory for JSON
    '''
    # Prefer provided export_dir or fallback to the central JSON_EXPORT_DIR
    directory = str(export_dir) if export_dir else str(settings.JSON_EXPORT_DIR)
    os.makedirs(directory, exist_ok=True)
    return directory

def parse_apify_timestamp(value):
    if not value:
        return timezone.now()

    if isinstance(value, datetime):
        parsed = value
    else:
        parsed = datetime.fromisoformat(value.replace('Z', '+00:00'))
        if timezone.is_naive(parsed):
            parsed = timezone.make_aware(parsed, timezone.utc)

    return parsed


def finalize_club_workflow(club_id, download_results=None):
    club = Club.objects.filter(id=club_id).first()
    if not club:
        return {'step': 'error', 'message': 'Club not found'}

    images_to_save = []
    for res in download_results or []:
        if res.get('status') == 'success':
            images_to_save.append(
                PostImage(
                    post_id=res['post_id'],
                    order=res['order'],
                    image=res['path'],
                )
            )

    if images_to_save:
        PostImage.objects.bulk_create(images_to_save)

    club.last_fetched_date = timezone.now()
    club.posts_count = club.posts.count()
    club.save(update_fields=['last_fetched_date', 'posts_count'])

    return {
        'step': 'complete',
        'club_id': str(club.id),
        'images_saved': len(images_to_save),
    }

# entry point to call from the Django application
def orchestrator(club_id, search_limit=20, max_items=50, export_dir=None, full_sync=False, only_posts_newer_than=None):
    workflow = chain(
        retrieve_json.s(club_id, search_limit, max_items, export_dir, full_sync, only_posts_newer_than),
        process.s(club_id, full_sync)
    )

    result = workflow.apply_async()
    return result.id


@shared_task(bind=True)
def retrieve_json(club_id, search_limit=20, max_items=50, export_dir=None, full_sync=False, only_posts_newer_than=None):
    club = Club.objects.filter(id=club_id).only('id', 'ig_handle', 'name').first()
    
    if not club:
        raise ValueError('Club not found')

    if not club.ig_handle:
        raise ValueError('Club does not have an Instagram handle')

    latest_timestamp = None
    if only_posts_newer_than is None:
        latest_timestamp = club.posts.order_by('-timestamp').values_list('timestamp', flat=True).first()

        if latest_timestamp is not None:
            if timezone.is_aware(latest_timestamp):
                latest_timestamp = latest_timestamp.astimezone(dt_timezone.utc)
            only_posts_newer_than = latest_timestamp.date().isoformat()

    export_dir = get_export_dir(export_dir)

    self.update_state(state='PROGRESS', meta={
        'message':'Running Apify actor',
        'club_id': str(club.id),
    })

    dataset = fetch_instagram_posts_via_apify(
        club.ig_handle, 
        search_limit=search_limit, 
        max_items=max_items,
        export_dir=export_dir,
        only_posts_newer_than=only_posts_newer_than
    )

    self.update_state(state='PROGRESS', meta={
        'message':'Successfully retrieved dataset from Apify',
        'club_id': str(club.id),
    })

    return dataset

@shared_task(bind=True)
def process(self, dataset, club_id, full_sync=False):
    club = Club.objects.filter(id=club_id).first()
    if not club:
        raise ValueError('Club not found')

    if full_sync:
        club.posts.all().delete()

    if not isinstance(dataset, list):
        dataset = []

    total_posts = len(dataset)
    image_download_tasks = []

    for index, item in enumerate(dataset):
        if not item:
            continue
        
        current_post = index + 1
        ig_id = item.get('id')
        if not ig_id:
            continue

        self.update_state(state='PROGRESS', meta={
            'message':f'Processing {current_post} of {total_posts} posts',
            'club_id': str(club.id)
        })

        short_code = item.get('shortCode', '')
        timestamp = parse_apify_timestamp(item.get('timestamp'))
        caption = item.get('caption', '')

        post, created = Post.objects.update_or_create(
            short_code = short_code,
            defaults={
                'club': club,
                'caption': caption,
                'timestamp': timestamp,
            }
        )

        image_urls = item.get('images') or ([item.get('displayUrl')] if item.get('displayUrl') else [])
        total_images_for_post = len(image_urls)

        for order, url in enumerate(image_urls):
            if not url:
                continue
            
            if PostImage.objects.filter(post=post, order=order).exists():
                continue

            image_download_tasks.append(download_image_worker.s(post.id, url, order, short_code, current_post, total_images_for_post))

    if image_download_tasks:
        chord(image_download_tasks)(finalize_workflow.s(club_id))
    else:
        finalize_club_workflow(club.id, [])

    return f'Processed {total_posts} posts. Fired {len(image_download_tasks)} image download tasks.'


@shared_task(bind=True)
def download_image_worker(self, post_id, image_url, order, short_code, current_post, total_images_for_post):
    current_image = order + 1

    self.update_state(state='PROGRESS', meta={
        'message': f'Downloading image {current_image} of {total_images_for_post} for post {current_post}',
        'post_id': post_id,
    })

    try:
        response = requests.get(image_url, timeout=10)
        response.raise_for_status()

        image_file = ContentFile(response.content)
        filename = f'{short_code}_{order}.jpg'
        post_image = PostImage(post_id=post_id, order=order)
        post_image.image.save(filename, image_file, save=False)

        return{
            'status': 'success',
            'post_id': post_id,
            'order': order,
            'path': post_image.image.name
        }

    except Exception as e:
        return {
            'status': 'error',
            'post_id': post_id,
            'order': order,
            'error': str(e)
        }

@shared_task(bind=True)
def finalize_workflow(self, download_results, club_id):
    return finalize_club_workflow(club_id, download_results)

    # self.update_state(
    #     state='PROGRESS', meta={
    #         'message':'Sending email',
    #         'club_id': str(club.id)
    #     }
    # )



# add.apply_async((1, 2), queue='testworker')
# show.apply_async((result,), queue='testworker')
