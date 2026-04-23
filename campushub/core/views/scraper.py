from datetime import datetime

from django.utils import timezone

from core.models import Post
from core.views.apify import run_actor_sync_get_dataset_items

IG_ACTOR_ID = "shu8hvrXbJbY3Eb9W"


def parse_apify_timestamp(value):
    if not value:
        return timezone.now()

    if isinstance(value, datetime):
        return value

    # Apify timestamps are usually ISO8601 with trailing Z.
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if timezone.is_naive(parsed):
        return timezone.make_aware(parsed, timezone.utc)
    return parsed


def fetch_instagram_posts(ig_handle, search_limit=20, max_items=50):
    payload = {
        "directUrls": [f"https://www.instagram.com/{ig_handle}/"],
        "resultsType": "posts",
        "searchLimit": search_limit,
        "searchType": "hashtag",
    }
    # `maxItems` caps billed dataset items for pay-per-result Actors,
    # while `limit` controls the maximum number of items returned by the endpoint.
    return run_actor_sync_get_dataset_items(
        IG_ACTOR_ID,
        payload,
        max_items=max_items,
        limit=max_items,
    )


def upsert_posts_for_club(club, items):
    created_count = 0

    for item in items:
        ig_id = item.get("id")
        if not ig_id:
            continue

        _, created = Post.objects.update_or_create(
            ig_id=ig_id,
            defaults={
                "club": club,
                "short_code": item.get("shortCode", ""),
                "caption": item.get("caption", "") or "",
                "image_url": item.get("displayUrl", "") or "",
                "timestamp": parse_apify_timestamp(item.get("timestamp")),
            },
        )
        if created:
            created_count += 1

    return created_count


def scrape_club(club, full_sync=False, search_limit=20, max_items=50):
    if not club.ig_handle:
        return 0

    data = fetch_instagram_posts(
        ig_handle=club.ig_handle,
        search_limit=search_limit,
        max_items=max_items,
    )

    if not isinstance(data, list):
        return 0

    if full_sync:
        club.posts.all().delete()
        items_to_save = data
    elif club.last_fetched_date:
        items_to_save = [
            item
            for item in data
            if parse_apify_timestamp(item.get("timestamp")) > club.last_fetched_date
        ]
    else:
        items_to_save = data

    created = upsert_posts_for_club(club, items_to_save)

    club.last_fetched_date = timezone.now()
    club.posts_count = club.posts.count()
    club.save(update_fields=["last_fetched_date", "posts_count"])

    return created


