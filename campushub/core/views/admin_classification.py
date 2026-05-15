import logging
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.decorators import user_passes_test
from django.core.paginator import Paginator

from core.models import Post, Club, Institution
from core.services.post_categorization import assign_category_to_post

logger = logging.getLogger(__name__)

def is_superuser(user):
    return user.is_authenticated and user.is_superuser

@user_passes_test(is_superuser)
def admin_classification_dashboard(request):
    # Handle multiple club IDs from the filter
    selected_university = request.GET.get('university')
    selected_clubs = request.GET.getlist('club_ids') or request.GET.getlist('club')
    date_sort = request.GET.get('sort', 'latest')
    status_filter = request.GET.get('status', '')
    per_page = request.GET.get('per_page', '20')
    
    posts = Post.objects.select_related('club', 'club__institution')

    # Apply Filters
    clean_club_ids = [cid for cid in selected_clubs if str(cid).isdigit()]
    if clean_club_ids:
        posts = posts.filter(club_id__in=clean_club_ids)
    elif selected_university:
        posts = posts.filter(club__institution_id=selected_university)

    if status_filter:
        posts = posts.filter(category=status_filter)

    # Apply Sorting
    if date_sort == 'oldest':
        posts = posts.order_by('timestamp')
    else:
        posts = posts.order_by('-timestamp')

    # Dynamic Pagination Size
    try:
        if per_page == 'all':
            page_size = posts.count() or 20 # Fallback to 20 if no posts
        else:
            page_size = int(per_page)
    except (ValueError, TypeError):
        page_size = 20

    paginator = Paginator(posts, page_size)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)


    universities = Institution.objects.all().order_by('university_name')

    # Smart grouped naming — same as Scraper Dashboard
    clubs_qs = Club.objects.select_related('institution').all().order_by('institution__university_name', 'name')
    name_counts = {}
    for c in clubs_qs:
        name_counts[c.name] = name_counts.get(c.name, 0) + 1

    grouped_clubs = {}
    for c in clubs_qs:
        inst_name = c.institution.university_name
        if inst_name not in grouped_clubs:
            grouped_clubs[inst_name] = []
        display_name = f"{c.name} ({inst_name})" if name_counts[c.name] > 1 else c.name
        grouped_clubs[inst_name].append({
            'id': c.id,
            'display_name': display_name,
            'search_key': f"{c.name} {inst_name}".lower()
        })

    context = {
        'page_obj': page_obj,
        'universities': universities,
        'grouped_clubs': grouped_clubs,
        'selected_university': int(selected_university) if selected_university else None,
        'selected_clubs': [int(c) for c in selected_clubs if str(c).isdigit()],
        'status_filter': status_filter,
        'date_sort': date_sort,
        'per_page': per_page,
    }




    # If it's an HTMX request, return only the table body and pagination
    if request.headers.get('HX-Request'):
        return render(request, 'admin_classification_partial.html', context)

    return render(request, 'admin_classification.html', context)


@user_passes_test(is_superuser)
def admin_bulk_classify(request):
    """Classifies all posts matching the current filters or selected clubs."""
    if request.method == 'POST':
        university_id = request.POST.get('university')
        # Handle multiple club IDs
        club_ids = request.POST.getlist('club_ids[]') or request.POST.getlist('club_ids')
        status_filter = request.POST.get('status')
        
        posts = Post.objects.filter(category='MISC')
        
        if club_ids:
            posts = posts.filter(club_id__in=club_ids)
        elif university_id:
            posts = posts.filter(club__institution_id=university_id)
            
        if status_filter:
            posts = posts.filter(category=status_filter)
            
        for post in posts:
            try:
                assign_category_to_post(post)
            except Exception as e:
                # Log but continue with others
                continue
            
        return HttpResponse(f'<script>window.location.reload();</script>')
        
    return HttpResponse('Invalid request', status=400)


@user_passes_test(is_superuser)
def admin_bulk_revert_classification(request):
    """Reverts classified posts back to MISC for selected clubs or across all clubs."""
    if request.method == 'POST':
        scope = request.POST.get('scope', 'selected')
        club_ids = request.POST.getlist('club_ids[]') or request.POST.getlist('club_ids')

        posts = Post.objects.exclude(category='MISC')

        if scope == 'all':
            reverted_count = posts.update(category='MISC')
        else:
            if not club_ids:
                return HttpResponse('No clubs selected for revert.', status=400)

            posts = posts.filter(club_id__in=club_ids)
            reverted_count = posts.update(category='MISC')

        logger.info(f"Bulk revert completed. Scope={scope}, reverted={reverted_count}")
        return HttpResponse(f'<script>window.location.reload();</script>')

    return HttpResponse('Invalid request', status=400)



@user_passes_test(is_superuser)
def admin_classify_post(request, post_id):
    if request.method == 'POST':
        post = get_object_or_404(Post, id=post_id)
        assign_category_to_post(post)
        
        # Return the full row fragment to update both the select and the button
        return render(request, 'admin_classification_row.html', {'post': post})
        
    return HttpResponse('Invalid request', status=400)

@user_passes_test(is_superuser)
def admin_update_post_category(request, post_id):
    if request.method == 'POST':
        post = get_object_or_404(Post, id=post_id)
        
        # Log for debugging
        new_category = request.POST.get('category') or request.GET.get('category')
        logger.info(f"Manual update request for post {post_id}. New category: {new_category}")
        
        if new_category:
            post.category = new_category
            post.save(update_fields=['category'])
            logger.info(f"Successfully updated post {post_id} to {new_category}")
        else:
            logger.warning(f"No category provided for post {post_id} update.")
            
        return render(request, 'admin_classification_row.html', {'post': post})

        
    return HttpResponse('Invalid request', status=400)


