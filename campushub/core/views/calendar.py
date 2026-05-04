from django.shortcuts import render
from core.models import Club, Institution, Post
from django.db.models import Q

def calendar(request):
    university = request.GET.get('university', '').strip()
    club = request.GET.get('club', '').strip()
    university_id = request.GET.get('university_id', '').strip()
    club_id = request.GET.get('club_id', '').strip()

    posts = Post.objects.select_related('club__institution').order_by('-timestamp')

    if university_id:
        posts = posts.filter(club__institution_id=university_id)
    elif university:
        posts = posts.filter(club__institution__university_name__icontains=university)

    if club_id:
        posts = posts.filter(club_id=club_id)
    elif club:
        posts = posts.filter(club__name__icontains=club)

    if not (university or club or university_id or club_id):
        posts = Post.objects.none()

    universities = list(Institution.objects.order_by('university_name').values('id', 'university_name'))
    all_clubs = list(Club.objects.order_by('name').values('id', 'name', 'institution_id'))

    if university_id:
        club_suggestions = list(
            Club.objects.filter(institution_id=university_id)
            .order_by('name')
            .values_list('name', flat=True)
            .distinct()
        )
    elif university:
        club_suggestions = list(
            Club.objects.filter(institution__university_name__icontains=university)
            .order_by('name')
            .values_list('name', flat=True)
            .distinct()
        )
    else:
        club_suggestions = list(
            Club.objects.order_by('name').values_list('name', flat=True).distinct()
        )

    return render(request, 'calendar.html', {
        'posts': posts,
        'university': university,
        'club': club,
        'university_id': university_id,
        'club_id': club_id,
        'universities': universities,
        'all_clubs': all_clubs,
        'club_suggestions': club_suggestions,
    })