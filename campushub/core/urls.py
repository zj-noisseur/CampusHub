from django.urls import path
from .import views 
from django.contrib.auth import views as auth_views

app_name = 'core'
urlpatterns = [
    # Auth & Profile
    path('', views.sign_up, name='home'),
    path('sign_up/', views.sign_up, name='sign_up'),
    path('claim/', views.claim_club, name='claim_club'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('profile/', views.user_profile, name='profile'),
    path('club/<int:club_id>/manager-dashboard/', views.manager_dashboard, name='manager_dashboard'),
    path('dashboard/member/<int:membership_id>/<str:action>/', views.process_membership, name='process_membership'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('club/<int:club_id>/join/', views.join_club, name='join_club'),
    path('club/<int:club_id>/apply-manager/', views.apply_manager, name='apply_manager'),
    #Choose a club

    #The Dashboard List
    path('club/<int:club_id>/', views.club_profile, name='club_profile'),
    path('club/<int:club_id>/dashboard/', views.club_admin_dashboard, name='club_admin_dashboard'),
    path('club/<int:club_id>/settings/', views.club_settings, name='club_settings'),
    path('club/<int:club_id>/event/<int:event_id>/', views.club_admin_dashboard, name='event_admin_dashboard'),
    path('dashboard/', views.student_dashboard, name='student_dashboard'),

    # The Core Features you want to show
    path('import-csv/<int:event_id>/', views.import_attendees_csv, name='import_csv'),
    path('download-certificates/<int:event_id>/', views.download_certificates, name='download_certificates'),
    path('download-my-certificate/<int:event_id>/', views.download_my_certificate, name='download_my_certificate'),

    #button to mark as ready and attanded
    path('event/<int:event_id>/toggle-ready/<str:prereg_id>/', views.toggle_ready_status, name='toggle_ready'),
    path('event/<int:event_id>/toggle-attended/<str:prereg_id>/', views.toggle_attended_status, name='toggle_attended'),

    path('event/<int:event_id>/set-status/<str:status>/', views.set_event_status, name='set_event_status'),
]