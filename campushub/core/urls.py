from django.urls import path
from core.views.directory import directory
from core.views.clubs import clubs
from core.views.universities import universities
from core.views.dashboard import dashboard_home, dashboard_action, dashboard_task_queue

from core.views.feed import feed

app_name = 'core'
urlpatterns = [
    path('directory/', directory, name='directory'),
    path('dashboard/', dashboard_home, name='dashboard_home'),
    path('dashboard/queue/', dashboard_task_queue, name='dashboard_task_queue'),
    path('dashboard/action/', dashboard_action, name='dashboard_action'),
    path('state/<int:state_id>/universities/', universities, name='universities'),
    path('state/<int:state_id>/universities/<int:university_id>/clubs/', clubs, name='clubs'),
    path('feed/', feed, name='feed'),
]