from django.urls import path
from core.views.directory import directory
from core.views.clubs import clubs
from core.views.universities import universities
from core.views.admin_dashboard import admin_dashboard_home, admin_dashboard_action, admin_dashboard_task_queue, admin_dashboard_task_status

from core.views.feed import feed

app_name = 'core'
urlpatterns = [
    path('directory/', directory, name='directory'),
    path('admin-site/dashboard/', admin_dashboard_home, name='admin_dashboard'),
    path('admin-site/dashboard/queue/', admin_dashboard_task_queue, name='admin_task_queue'),
    path('admin-site/dashboard/task-status/', admin_dashboard_task_status, name='admin_task_status'),
    path('admin-site/dashboard/action/', admin_dashboard_action, name='admin_action'),
    path('state/<int:state_id>/universities/', universities, name='universities'),
    path('state/<int:state_id>/universities/<int:university_id>/clubs/', clubs, name='clubs'),
    path('feed/', feed, name='feed'),
]