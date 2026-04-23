import json
import os
from datetime import datetime

import requests
from django.core.files.base import ContentFile
from django.utils import timezone

from core.models import Post, PostImage
from core.views.apify import fetch_instagram_posts_via_apify

EXPORT_BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), 'export'))


def get_export_dir(export_dir=None):
    directory = export_dir or EXPORT_BASE_DIR
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


def process_club_dataset(club, dataset):
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
    club.save(update_fields=['last_fetched_date'])

    return None


def run_club_scrape_task(club, search_limit=20, max_items=50, export_dir=None):
    if not club.ig_handle:
        raise ValueError('Club does not have an Instagram handle')

    export_dir = get_export_dir(export_dir)
    dataset = fetch_instagram_posts_via_apify(
        club.ig_handle,
        search_limit=search_limit,
        max_items=max_items,
        export_dir=export_dir,
    )

    created_count = 0
    if isinstance(dataset, list):
        created_count = process_club_dataset(club, dataset)

    return {
        'club_id': str(club.id),
        'ig_handle': club.ig_handle,
        'items_returned': len(dataset) if isinstance(dataset, list) else None,
        'created_count': created_count,
        'export_dir': export_dir,
    }
