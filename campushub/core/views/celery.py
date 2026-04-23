import json
import os
from datetime import datetime
from dotenv import load_dotenv
import requests
from django.core.files.base import ContentFile
from django.conf import settings
from django.utils import timezone
from core.models import Post, PostImage

load_dotenv()

url = "https://api.apify.com/v2/acts"
IG_ACTOR_ID = "shu8hvrXbJbY3Eb9W"
JSON_EXPORT_DIR = os.path.abspath(os.fspath(settings.JSON_EXPORT_DIR))

# general structure for executing Apify actor
def runActor(actorId, input_payload, timeout=None, memory=None, max_items=None, max_total_charge_usd=None, format="json", clean=False, offset=0, limit=None, fields=None, omit=None):
    """
    Run an actor synchronously and retrieve dataset items.

    :param actorId: The ID of the actor to run.
    :param input_payload: The input payload for the actor.
    :param timeout: Timeout for the run in seconds (set to None for now).
    :param memory: Memory limit for the run in MB (optional).
    :param max_items: Maximum number of dataset items to charge for (optional).
    :param max_total_charge_usd: Maximum cost of the run in USD (optional).
    :param format: Format of the dataset items (default: "json").
    :param clean: Whether to return only non-empty items and skip hidden fields (default: False).
    :param offset: Number of items to skip at the start (default: 0).
    :param limit: Maximum number of items to return (optional).
    :param fields: Comma-separated list of fields to include in the output (optional).
    :param omit: Comma-separated list of fields to omit from the output (optional).
    :return: The dataset items from the actor run.
    """
    headers = {
        'Accept': 'application/json',
        'Authorization': f"Bearer {os.getenv('APIFY_API_KEY')}"
    }

    params = {
        'timeout': timeout,
        'memory': memory,
        'maxItems': max_items,
        'maxTotalChargeUsd': max_total_charge_usd,
        'format': format,
        'clean': int(clean),
        'offset': offset,
        'limit': limit,
        'fields': fields,
        'omit': omit
    }

    # Remove None values from params
    params = {k: v for k, v in params.items() if v is not None}

    request_url = f"{url}/{actorId}/run-sync-get-dataset-items"
    response = requests.post(request_url, headers=headers, json=input_payload, params=params)

    if response.status_code == 201:
        return response.json()
    else:
        raise Exception(f"Failed to run actor and get dataset items: {response.status_code} - {response.text}")


def exportDataset(dataset, ig_handle):
    os.makedirs(JSON_EXPORT_DIR, exist_ok=True)
    file_path = os.path.join(JSON_EXPORT_DIR, f"{ig_handle}.json")
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(dataset, f, ensure_ascii=False, indent=4)
    return file_path

def fetchInstaPost(ig_handle, search_limit=20, max_items=50, actor_id=IG_ACTOR_ID):
    payload = {
        'directUrls': [f'https://www.instagram.com/{ig_handle}/'],
        'resultsType': 'posts',
        'searchLimit': search_limit,
    }

    dataset = runActor(
        actor_id, 
        payload, 
        max_items = max_items,
        limit = max_items,
    )

    exportDataset(dataset, ig_handle)
    return dataset


def parseTimestamp(value):
    if not value:
        return timezone.now()

    if isinstance(value, datetime):
        parsed = value
    else:
        parsed = datetime.fromisoformat(value.replace('Z', '+00:00'))
        if timezone.is_naive(parsed):
            parsed = timezone.make_aware(parsed, timezone.utc)

    return parsed


def processDataset(club, dataset):

    created_count = 0

    for item in dataset:
        ig_id = item.get('id')
        if not ig_id:
            continue

        short_code = item.get('shortCode', '')
        timestamp = parseTimestamp(item.get('timestamp'))
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

        if created:
            created_count += 1

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

    return created_count
