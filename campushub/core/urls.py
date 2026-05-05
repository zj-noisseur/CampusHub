from django.urls import path
from django.contrib.auth import views as auth_views

from core.views.directory import directory
from core.views.clubs import clubs
from core.views.universities import universities
from core.views.admin_dashboard import admin_dashboard_home, admin_dashboard_action, admin_dashboard_task_queue, admin_dashboard_task_status
from core.views.feed import feed
from core.views.sign_up import sign_up
from core.views.claim_club import claim_club
from core.views.profile import user_profile, edit_profile
from core.views.calendar import calendar
from core.views.club_actions import join_club, apply_manager
from core.views.manager_dashboard import manager_dashboard, process_membership
from core.views.dashboards import club_profile, club_admin_dashboard, club_settings, student_dashboard, toggle_ready_status, toggle_attended_status, set_event_status
from core.views.imports import import_attendees_csv
from core.views.certificates import download_certificates, download_my_certificate

app_name = 'core'
urlpatterns = [
    path('', feed, name='home'),
    path('directory/', directory, name='directory'),
    path('admin-site/dashboard/', admin_dashboard_home, name='admin_dashboard'),
    path('admin-site/dashboard/queue/', admin_dashboard_task_queue, name='admin_task_queue'),
    path('admin-site/dashboard/task-status/', admin_dashboard_task_status, name='admin_task_status'),
    path('admin-site/dashboard/action/', admin_dashboard_action, name='admin_action'),
    path('state/<int:state_id>/universities/', universities, name='universities'),
    path('state/<int:state_id>/universities/<int:university_id>/clubs/', clubs, name='clubs'),
    path('feed/', feed, name='feed'),
    path('signup/', sign_up, name='signup'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='core:feed'), name='logout'),
    path('profile/', user_profile, name='profile'),
    path('profile/edit/', edit_profile, name='edit_profile'),
    path('profile/manager/<int:club_id>/', manager_dashboard, name='manager_dashboard'),
    path('club/<int:club_id>/admin/', club_admin_dashboard, name='club_admin_dashboard'),
    path('club/<int:club_id>/settings/', club_settings, name='club_settings'),
    path('student/dashboard/', student_dashboard, name='student_dashboard'),
    path('membership/<int:membership_id>/<str:action>/', process_membership, name='process_membership'),
    path('event/<int:event_id>/toggle-ready/<int:prereg_id>/', toggle_ready_status, name='toggle_ready_status'),
    path('event/<int:event_id>/toggle-attended/<int:prereg_id>/', toggle_attended_status, name='toggle_attended_status'),
    path('event/<int:event_id>/set-status/<str:status>/', set_event_status, name='set_event_status'),
    path('event/<int:event_id>/import-attendees/', import_attendees_csv, name='import_attendees_csv'),
    path('event/<int:event_id>/download-certificates/', download_certificates, name='download_certificates'),
    path('event/<int:event_id>/download-certificate/', download_my_certificate, name='download_my_certificate'),
    path('calendar/', calendar, name='calendar'),
    path('club/<int:club_id>/', club_profile, name='club_profile'),
    path('club/<int:club_id>/join/', join_club, name='join_club'),
    path('club/<int:club_id>/apply-manager/', apply_manager, name='apply_manager'),
]
