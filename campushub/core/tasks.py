import json
import os
from datetime import datetime, timezone as dt_timezone

import requests
from django.core.files.base import ContentFile
from django.db import transaction
from django.utils import timezone

from celery import shared_task, current_task
import time

from django.conf import settings
from core.models import Club, Post, PostImage
from core.views.apify import fetch_instagram_posts_via_apify

def get_export_dir(export_dir=None):
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


def process_club_dataset(club, dataset, full_sync=False):
    if full_sync:
        club.posts.all().delete()

    # created_count = 0

    for item in dataset:
        ig_id = item.get('id')
        if not ig_id:
            continue

        short_code = item.get('shortCode', '')
        timestamp = parse_apify_timestamp(item.get('timestamp'))
        caption = item.get('caption', '') or ''
        image_urls = item.get('images') or ([item.get('displayUrl')] if item.get('displayUrl') else [])

        post, created = Post.objects.update_or_create(
            short_code=short_code,
            defaults={
                'club': club,
                'caption': caption,
                'timestamp': timestamp,
            }
        )

        # if created:
        #     created_count += 1

        for order, image_url in enumerate(image_urls):
            if not image_url:
                continue

            if PostImage.objects.filter(post=post, order=order).exists():
                continue

            try:
                response = requests.get(image_url, timeout=10)
                response.raise_for_status()
                image_file = ContentFile(response.content)
                post_image = PostImage(post=post, order=order)
                post_image.image.save(f'{short_code}_{order}.jpg', image_file)
            except Exception:
                continue

    club.last_fetched_date = timezone.now()
    club.posts_count = club.posts.count()
    club.save(update_fields=['last_fetched_date', 'posts_count'])

    # return created_count

@shared_task(bind=True)
def run_club_scrape_task(self, club_id, search_limit=20, max_items=50, export_dir=None, full_sync=False, only_posts_newer_than=None):
    club = Club.objects.filter(id=club_id).only('id', 'ig_handle', 'name').first()
    if not club:
        raise ValueError('Club not found')

    if not club.ig_handle:
        raise ValueError('Club does not have an Instagram handle')

    if only_posts_newer_than is None:
        latest_timestamp = club.posts.order_by('-timestamp').values_list('timestamp', flat=True).first()
        if latest_timestamp is not None:
            if timezone.is_aware(latest_timestamp):
                latest_timestamp = latest_timestamp.astimezone(dt_timezone.utc)
            only_posts_newer_than = latest_timestamp.date().isoformat()

    export_dir = get_export_dir(export_dir)

    # celery method to keep track of task
    self.update_state(state='PROGRESS', meta={
        'status': 'Fetching from Apify...', 
        'progress': 0, 
        'club_id': str(club.id),
        'club_name': club.name
    })

    dataset = fetch_instagram_posts_via_apify(
        club.ig_handle,
        search_limit=search_limit,
        max_items=max_items,
        export_dir=export_dir,
        only_posts_newer_than=only_posts_newer_than,
    )

    self.update_state(state='PROGRESS', meta={
        'status': 'Queuing database write...',
        'progress': 50,
        'club_id': str(club.id),
        'club_name': club.name
    })

    write_task = persist_club_dataset.apply_async(
        (str(club.id), dataset, full_sync),
        queue='db_write'
    )

    return {
        'club_id': str(club.id),
        'ig_handle': club.ig_handle,
        'items_returned': len(dataset) if isinstance(dataset, list) else None,
        'export_dir': export_dir,
        'db_write_task_id': write_task.id,
    }


@shared_task(bind=True)
def persist_club_dataset(self, club_id, dataset, full_sync=False):
    club = Club.objects.filter(id=club_id).only('id', 'ig_handle', 'name').first()
    if not club:
        raise ValueError('Club not found')

    self.update_state(state='PROGRESS', meta={
        'status': 'Writing dataset to database...',
        'progress': 0,
        'club_id': str(club.id),
        'club_name': club.name
    })

    with transaction.atomic():
        process_club_dataset(club, dataset, full_sync=full_sync)

    self.update_state(state='PROGRESS', meta={
        'status': 'Database write complete',
        'progress': 100,
        'club_id': str(club.id),
        'club_name': club.name
    })

    return {
        'club_id': str(club.id),
        'items_processed': len(dataset) if isinstance(dataset, list) else 0,
        'full_sync': full_sync,
    }
