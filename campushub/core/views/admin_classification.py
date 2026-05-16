import logging
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.decorators import user_passes_test
from django.core.paginator import Paginator

from core.models import Post, Club, Institution
from core.services.post_categorization import assign_category_to_post, assign_event_status_to_post

logger = logging.getLogger(__name__)

def is_superuser(user):
    return user.is_authenticated and user.is_superuser

# --- SHARED HELPERS ---

def get_dashboard_context(request, posts_qs):
    """Helper to handle common filtering and pagination logic."""
    selected_university = request.GET.get('university')
    selected_clubs = request.GET.getlist('club_ids') or request.GET.getlist('club')
    date_sort = request.GET.get('sort', 'latest')
    per_page = request.GET.get('per_page', '20')
    
    posts = posts_qs.select_related('club', 'club__institution')

    # Apply Filters
    clean_club_ids = [cid for cid in selected_clubs if str(cid).isdigit()]
    if clean_club_ids:
        posts = posts.filter(club_id__in=clean_club_ids)
    elif selected_university:
        posts = posts.filter(club__institution_id=selected_university)

    # Apply Sorting
    if date_sort == 'oldest':
        posts = posts.order_by('timestamp')
    else:
        posts = posts.order_by('-timestamp')

    # Dynamic Pagination Size
    try:
        if per_page == 'all':
            page_size = posts.count() or 20
        else:
            page_size = int(per_page)
    except (ValueError, TypeError):
        page_size = 20

    paginator = Paginator(posts, page_size)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    universities = Institution.objects.all().order_by('university_name')

    # Grouped Club List
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

    return {
        'page_obj': page_obj,
        'universities': universities,
        'grouped_clubs': grouped_clubs,
        'selected_university': int(selected_university) if selected_university else None,
        'selected_clubs': [int(c) for c in selected_clubs if str(c).isdigit()],
        'date_sort': date_sort,
        'per_page': per_page,
    }

# --- STEP 1: TEMPORAL CLASSIFICATION ---

@user_passes_test(is_superuser)
def admin_temporal_classification_dashboard(request):
    """Step 1: Filter between upcoming events and non-events."""
    status_filter = request.GET.get('status', '') # '', 'True', 'False'
    posts = Post.objects.all()
    
    if status_filter == 'True':
        posts = posts.filter(is_event=True)
    elif status_filter == 'False':
        posts = posts.filter(is_event=False)
    elif status_filter == 'PENDING':
        posts = posts.filter(is_event__isnull=True)

    context = get_dashboard_context(request, posts)
    context['status_filter'] = status_filter

    if request.headers.get('HX-Request'):
        return render(request, 'admin_temporal_classification_partial.html', context)
    return render(request, 'admin_temporal_classification.html', context)

@user_passes_test(is_superuser)
def admin_classify_post_temporal(request, post_id):
    if request.method == 'POST':
        post = get_object_or_404(Post, id=post_id)
        assign_event_status_to_post(post)
        return render(request, 'admin_temporal_classification_row.html', {'post': post})
    return HttpResponse('Invalid request', status=400)

@user_passes_test(is_superuser)
def admin_update_post_event_status(request, post_id):
    if request.method == 'POST':
        post = get_object_or_404(Post, id=post_id)
        val = request.POST.get('is_event') or request.GET.get('is_event')
        if val == 'True':
            post.is_event = True
        elif val == 'False':
            post.is_event = False
        elif val == 'None':
            post.is_event = None
        post.save(update_fields=['is_event'])
        return render(request, 'admin_temporal_classification_row.html', {'post': post})
    return HttpResponse('Invalid request', status=400)

@user_passes_test(is_superuser)
def admin_bulk_temporal_classify(request):
    if request.method == 'POST':
        club_ids = request.POST.getlist('club_ids[]') or request.POST.getlist('club_ids')
        posts = Post.objects.filter(is_event__isnull=True)
        if club_ids:
            posts = posts.filter(club_id__in=club_ids)
            
        for post in posts:
            try:
                assign_event_status_to_post(post)
            except: continue
        return HttpResponse('<script>window.location.reload();</script>')
    return HttpResponse('Invalid request', status=400)

# --- STEP 2: EVENT CLASSIFICATION ---

@user_passes_test(is_superuser)
def admin_event_classification_dashboard(request):
    """Step 2: Categorize posts identified as events in Step 1."""
    status_filter = request.GET.get('status', '')
    posts = Post.objects.filter(is_event=True)
    
    if status_filter:
        posts = posts.filter(category=status_filter)

    context = get_dashboard_context(request, posts)
    context['status_filter'] = status_filter

    if request.headers.get('HX-Request'):
        return render(request, 'admin_event_classification_partial.html', context)
    return render(request, 'admin_event_classification.html', context)

@user_passes_test(is_superuser)
def admin_classify_post_event(request, post_id):
    if request.method == 'POST':
        post = get_object_or_404(Post, id=post_id)
        assign_category_to_post(post)
        return render(request, 'admin_event_classification_row.html', {'post': post})
    return HttpResponse('Invalid request', status=400)

@user_passes_test(is_superuser)
def admin_update_post_event_category(request, post_id):
    if request.method == 'POST':
        post = get_object_or_404(Post, id=post_id)
        new_category = request.POST.get('category') or request.GET.get('category')
        if new_category:
            post.category = new_category
            post.save(update_fields=['category'])
        return render(request, 'admin_event_classification_row.html', {'post': post})
    return HttpResponse('Invalid request', status=400)

@user_passes_test(is_superuser)
def admin_bulk_event_classify(request):
    if request.method == 'POST':
        club_ids = request.POST.getlist('club_ids[]') or request.POST.getlist('club_ids')
        posts = Post.objects.filter(is_event=True, category='MISC')
        if club_ids:
            posts = posts.filter(club_id__in=club_ids)
            
        for post in posts:
            try:
                assign_category_to_post(post)
            except: continue
        return HttpResponse('<script>window.location.reload();</script>')
    return HttpResponse('Invalid request', status=400)

# --- STEP 3: DATE EXTRACTION (PLACEHOLDER) ---

@user_passes_test(is_superuser)
def admin_date_extraction_dashboard(request):
    """Step 3: Placeholder for GLiNER-based date extraction."""
    return render(request, 'admin_date_extraction.html', {'placeholder': True})

# --- SHARED BULK ACTIONS ---

@user_passes_test(is_superuser)
def admin_bulk_revert_classification(request):
    """Universal revert based on step."""
    if request.method == 'POST':
        scope = request.POST.get('scope', 'selected')
        step = request.POST.get('step', 'event') # 'temporal' or 'event'
        club_ids = request.POST.getlist('club_ids[]') or request.POST.getlist('club_ids')

        if step == 'temporal':
            posts = Post.objects.all()
            if scope == 'all':
                posts.update(is_event=None)
            else:
                posts.filter(club_id__in=club_ids).update(is_event=None)
        else:
            posts = Post.objects.filter(is_event=True)
            if scope == 'all':
                posts.update(category='MISC')
            else:
                posts.filter(club_id__in=club_ids).update(category='MISC')

        return HttpResponse('<script>window.location.reload();</script>')
    return HttpResponse('Invalid request', status=400)
