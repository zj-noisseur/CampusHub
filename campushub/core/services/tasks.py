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
from django.db.models import F
from django.utils import timezone
from django.core.files.base import ContentFile

from celery import shared_task, chain, chord

from core.models import Club, ClubScrapeStatus, Post, PostImage
from core.views.apify import fetch_instagram_posts_via_apify, fetch_single_instagram_post_via_apify

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



def _get_or_create_scrape_status(club_id, defaults=None):
    defaults = defaults or {}
    defaults.setdefault('started_at', timezone.now())
    status, _ = ClubScrapeStatus.objects.get_or_create(club_id=club_id, defaults=defaults)
    return status


def update_scrape_status(
    club_id,
    task_id=None,
    task_name=None,
    state=None,
    phase=None,
    status=None,
    current_item=None,
    total_items=None,
    current_image=None,
    total_images=None,
    success_count=None,
    failure_count=None,
    finished=False,
    extra=None,
    failed_items_to_append=None,
):
    defaults = {'started_at': timezone.now()}
    status_obj, created = ClubScrapeStatus.objects.get_or_create(club_id=club_id, defaults=defaults)
    updates = {}
    if task_id is not None:
        updates['task_id'] = task_id
    if task_name is not None:
        updates['latest_task_name'] = task_name
    if state is not None:
        updates['state'] = state
    if phase is not None:
        updates['phase'] = phase
    if status is not None:
        updates['status'] = status
    if current_item is not None:
        updates['current_item'] = current_item
    if total_items is not None:
        updates['total_items'] = total_items
    if current_image is not None:
        updates['current_image'] = current_image
    if total_images is not None:
        updates['total_images'] = total_images
    if success_count is not None:
        updates['success_count'] = success_count
    if failure_count is not None:
        updates['failure_count'] = failure_count
    if finished:
        updates['finished_at'] = timezone.now()
    if extra is not None:
        updates['extra'] = extra

    if updates:
        ClubScrapeStatus.objects.filter(club_id=club_id).update(**updates)
        
    if failed_items_to_append:
        current_failed = status_obj.failed_items or []
        current_failed.extend(failed_items_to_append)
        ClubScrapeStatus.objects.filter(club_id=club_id).update(failed_items=current_failed)
        
    return status_obj


def increment_scrape_counts(club_id, success=False, failure=False, current_image_increment=0):
    updates = {}
    if success:
        updates['success_count'] = F('success_count') + 1
    if failure:
        updates['failure_count'] = F('failure_count') + 1
    if current_image_increment:
        updates['current_image'] = F('current_image') + current_image_increment
    if updates:
        ClubScrapeStatus.objects.filter(club_id=club_id).update(**updates)
    return


def finalize_club_workflow(club_id, download_results=None):
    club = Club.objects.filter(id=club_id).first()
    if not club:
        return {'step': 'error', 'message': 'Club not found'}

    images_to_save = []
    failed_items = []
    for res in download_results or []:
        if res.get('status') == 'success':
            images_to_save.append(
                PostImage(
                    post_id=res['post_id'],
                    order=res['order'],
                    image=res['path'],
                )
            )
        else:
            failed_items.append({
                'post_id': res.get('post_id'),
                'short_code': res.get('short_code'),
                'order': res.get('order'),
                'post_url': f"https://www.instagram.com/p/{res.get('short_code')}/" if res.get('short_code') else None,
                'error': res.get('error')
            })

    if images_to_save:
        PostImage.objects.bulk_create(images_to_save)

    club.last_fetched_date = timezone.now()
    club.posts_count = club.posts.count()
    club.save(update_fields=['last_fetched_date', 'posts_count'])

    success_count = sum(1 for res in download_results or [] if res.get('status') == 'success')
    failure_count = sum(1 for res in download_results or [] if res.get('status') != 'success')
    summary = {
        'images_saved': len(images_to_save),
        'success_count': success_count,
        'failure_count': failure_count,
        'downloaded_images': len(download_results or []),
    }
    update_scrape_status(
        club_id=club.id,
        task_id=None,
        task_name='finalize_workflow',
        state='SUCCESS',
        phase='finalized',
        status='Club scrape completed',
        current_item=len(images_to_save),
        total_items=len(images_to_save),
        current_image=len(download_results or []),
        total_images=len(download_results or []),
        success_count=success_count,
        failure_count=failure_count,
        finished=True,
        extra=summary,
        failed_items_to_append=failed_items
    )

    return {
        'step': 'complete',
        'club_id': str(club.id),
        'images_saved': len(images_to_save),
        'summary': summary,
    }

# entry point to call from the Django application
def orchestrator(club_id, search_limit=20, max_items=50, export_dir=None, full_sync=False, only_posts_newer_than=None):
    workflow = chain(
        retrieve_json.si(
            club_id=club_id,
            search_limit=search_limit,
            max_items=max_items,
            export_dir=export_dir,
            full_sync=full_sync,
            only_posts_newer_than=only_posts_newer_than,
        ),
        process.s(club_id, full_sync)
    )

    result = workflow.apply_async()
    return result.id


def orchestrator_retry_post(club_id, post_url):
    workflow = chain(
        retrieve_single_post_json.si(club_id=club_id, post_url=post_url),
        process.s(club_id, full_sync=False)
    )
    result = workflow.apply_async()
    return result.id


@shared_task(bind=True)
def retrieve_json(self, club_id, search_limit=20, max_items=50, export_dir=None, full_sync=False, only_posts_newer_than=None, *unexpected_args, **unexpected_kwargs):
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

    update_scrape_status(
        club.id,
        task_id=self.request.id,
        task_name='retrieve_json',
        state='PROGRESS',
        phase='apify',
        status='Running Apify actor',
    )
    self.update_state(state='PROGRESS', meta={
        'phase': 'apify',
        'status': 'Running Apify actor',
        'club_id': str(club.id),
    })

    dataset = fetch_instagram_posts_via_apify(
        club.ig_handle, 
        search_limit=search_limit, 
        max_items=max_items,
        export_dir=export_dir,
        only_posts_newer_than=only_posts_newer_than
    )

    update_scrape_status(
        club.id,
        state='PROGRESS',
        phase='apify',
        status='Successfully retrieved dataset from Apify',
    )
    self.update_state(state='PROGRESS', meta={
        'phase': 'apify',
        'status': 'Successfully retrieved dataset from Apify',
        'club_id': str(club.id),
    })

    return dataset

@shared_task(bind=True)
def retrieve_single_post_json(self, club_id, post_url):
    club = Club.objects.filter(id=club_id).only('id', 'name').first()
    
    if not club:
        raise ValueError('Club not found')

    update_scrape_status(
        club.id,
        task_id=self.request.id,
        task_name='retrieve_single_post_json',
        state='PROGRESS',
        phase='apify',
        status='Running Apify for single post',
    )
    self.update_state(state='PROGRESS', meta={
        'phase': 'apify',
        'status': 'Running Apify for single post',
        'club_id': str(club.id),
    })

    dataset = fetch_single_instagram_post_via_apify(post_url)

    update_scrape_status(
        club.id,
        state='PROGRESS',
        phase='apify',
        status='Successfully retrieved post from Apify',
    )
    self.update_state(state='PROGRESS', meta={
        'phase': 'apify',
        'status': 'Successfully retrieved post from Apify',
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
    total_images = 0
    for item in dataset:
        if not item:
            continue
        image_urls = item.get('images') or ([item.get('displayUrl')] if item.get('displayUrl') else [])
        total_images += len(image_urls)

    image_download_tasks = []
    queued_images = 0

    for index, item in enumerate(dataset):
        if not item:
            continue
        
        current_post = index + 1
        ig_id = item.get('id')
        if not ig_id:
            continue

        update_scrape_status(
            club.id,
            task_id=self.request.id,
            task_name='process',
            state='PROGRESS',
            phase='processing_posts',
            status=f'Processing {current_post} of {total_posts} posts',
            current_item=current_post,
            total_items=total_posts,
            current_image=queued_images,
            total_images=total_images,
        )
        self.update_state(state='PROGRESS', meta={
            'phase': 'processing_posts',
            'status': f'Processing {current_post} of {total_posts} posts',
            'current_item': current_post,
            'total_items': total_posts,
            'current_image': queued_images,
            'total_images': total_images,
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
        
        # Trigger AI classification for new posts or those that are still uncategorized
        if created or post.category == 'MISC':
            try:
                post.classify_category()
            except Exception as e:
                # Log error but don't fail the whole scrape task
                logger.error(f"Auto-classification failed for post {short_code}: {e}")


        image_urls = item.get('images') or ([item.get('displayUrl')] if item.get('displayUrl') else [])
        total_images_for_post = len(image_urls)

        for order, url in enumerate(image_urls):
            if not url:
                continue
            
            if PostImage.objects.filter(post=post, order=order).exists():
                continue

            queued_images += 1
            image_download_tasks.append(download_image_worker.s(
                post.id,
                url,
                order,
                short_code,
                current_post,
                total_images_for_post,
            ))

    if image_download_tasks:
        finalize_result = chord(image_download_tasks)(finalize_workflow.s(club_id))
    else:
        finalize_club_workflow(club.id, [])
        finalize_result = None

    return {
        'phase': 'processing_posts',
        'status': f'Processed {total_posts} posts. Fired {queued_images} image download tasks.',
        'current_item': total_posts,
        'total_items': total_posts,
        'current_image': queued_images,
        'total_images': total_images,
        'db_write_task_id': finalize_result.id if finalize_result else None,
        'club_id': str(club.id),
    }


@shared_task(bind=True)
def download_image_worker(self, post_id, image_url, order, short_code, current_post, total_images_for_post):
    current_image = order + 1

    post = Post.objects.filter(id=post_id).only('club_id').first()
    club_id = post.club_id if post else None

    if club_id:
        update_scrape_status(
            club_id,
            task_id=self.request.id,
            task_name='download_image_worker',
            state='PROGRESS',
            phase='downloading',
            status=f'Downloading image {current_image} of {total_images_for_post} for post {current_post}',
            current_item=current_post,
            current_image=current_image,
        )

    self.update_state(state='PROGRESS', meta={
        'phase': 'downloading',
        'status': f'Downloading image {current_image} of {total_images_for_post} for post {current_post}',
        'current_item': current_post,
        'total_items': 0,
        'current_image': current_image,
        'total_images': total_images_for_post,
        'post_id': post_id,
        'club_id': str(club_id) if club_id else None,
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
            'short_code': short_code,
            'error': str(e)
        }

@shared_task(bind=True)
def finalize_workflow(self, download_results, club_id):
    # download_results may be nested (list of batches) or a flat list; normalize to flat list
    valid_results = []
    for res in (download_results or []):
        if isinstance(res, dict):
            valid_results.append(res)
        elif isinstance(res, list):
            for r in res:
                if isinstance(r, dict):
                    valid_results.append(r)
    update_scrape_status(
        club_id,
        task_id=self.request.id,
        task_name='finalize_workflow',
        state='PROGRESS',
        phase='db_write',
        status='Writing images to database...',
        current_item=len(valid_results),
        total_items=len(valid_results),
        current_image=len(valid_results),
        total_images=len(valid_results),
    )
    
    self.update_state(state='PROGRESS', meta={
        'phase': 'db_write',
        'status': 'Writing images to database...',
        'current_item': len(valid_results),
        'total_items': len(valid_results),
        'current_image': len(valid_results),
        'total_images': len(valid_results),
        'club_id': str(club_id),
    })

    return finalize_club_workflow(club_id, valid_results)

    # self.update_state(
    #     state='PROGRESS', meta={
    #         'message':'Sending email',
    #         'club_id': str(club.id)
    #     }
    # )


# add.apply_async((1, 2), queue='testworker')
# show.apply_async((result,), queue='testworker')
