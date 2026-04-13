from django.core.paginator import Paginator
from django.shortcuts import render

from core.models import Club, Post


def feed(request):
    selected_club = request.GET.get("club")

    posts = Post.objects.select_related(
        "club",
        "club__institution",
        "club__institution__state",
    ).order_by("-timestamp")

    clubs = Club.objects.filter(ig_handle__isnull=False).exclude(ig_handle="").order_by("name")

    if selected_club:
        posts = posts.filter(club_id=selected_club)

    paginator = Paginator(posts, 20)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        "feed.html",
        {
            "page_obj": page_obj,
            "clubs": clubs,
            "selected_club": selected_club,
        },
    )

    
