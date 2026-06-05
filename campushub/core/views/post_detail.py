from django.shortcuts import render, get_object_or_404
from core.models import Post

def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    template_name = 'post_detail_partial.html' if request.headers.get('HX-Request') else 'post_detail.html'
    return render(request, template_name, {'post': post})
