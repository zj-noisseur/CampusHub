from django.core.paginator import Paginator
from django.shortcuts import render
from django.db.models import Prefetch, Q
from core.models import Club, Post, PostImage, Institution

def feed(request):
    selected_clubs = request.GET.getlist("club") or request.GET.getlist("club_ids")
    selected_category = request.GET.get("category", "all_events")
    search_query = request.GET.get("search", "")

    posts = Post.objects.select_related(
        "club",
        "club__institution",
        "club__institution__state",
    ).prefetch_related(
        Prefetch( 
            "postimage_set",
            queryset=PostImage.objects.order_by("order"),
            to_attr="images",
        )
    )

    # Filter logic
    clean_club_ids = [cid for cid in selected_clubs if str(cid).isdigit()]
    if clean_club_ids:
        posts = posts.filter(club_id__in=clean_club_ids)
    
    if selected_category == "all_events":
        posts = posts.filter(
            Q(is_event=True) | 
            Q(event__isnull=False) | 
            Q(category__in=['RECRUITMENT', 'COMPETITION', 'WORKSHOP', 'INDUSTRIAL_VISIT'])
        ).exclude(is_event=False)
    elif selected_category == "all":
        # Show all posts, no category filtering
        pass
    elif selected_category:
        posts = posts.filter(category=selected_category)
        
    if search_query:
        posts = posts.filter(club__name__icontains=search_query)

    posts = posts.order_by("-timestamp")

    paginator = Paginator(posts, 20)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    # Smart grouped naming — same as Scraper Dashboard
    clubs_qs = Club.objects.select_related('institution').filter(
        ig_handle__isnull=False
    ).exclude(ig_handle="").order_by('institution__university_name', 'name')

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

    return render(
        request,
        "feed.html",
        {
            "page_obj": page_obj,
            "grouped_clubs": grouped_clubs,
            "selected_clubs": [int(c) for c in selected_clubs if str(c).isdigit()],
            "selected_category": selected_category,
            "search_query": search_query,
            "categories": Post.CATEGORY_CHOICES,
        },
    )
