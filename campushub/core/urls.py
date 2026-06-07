from django.urls import path
from django.contrib.auth import views as auth_views
from core.views.directory import directory
from core.views.clubs import clubs
from core.views.universities import universities
from core.views.admin_dashboard import admin_dashboard_home, admin_dashboard_action, admin_dashboard_task_queue, admin_dashboard_task_status
from core.views import admin_classification as ac
from core.views.feed import feed
from core.views.sign_up import sign_up, activate_account
from core.views.claim_club import claim_club
from core.views.profile import user_profile, edit_profile
from core.views.calendar import calendar
from core.views.club_actions import join_club, apply_manager
from core.views.manager_dashboard import manager_dashboard, process_membership
from core.views.imports import import_attendees_csv
from core.views.certificates import upload_certificate_template, download_certificates, download_my_certificate
from core.views.dashboards import club_profile, club_admin_dashboard, club_settings, student_dashboard, toggle_ready_status, toggle_attended_status, set_event_status, create_event, edit_event, my_events
from core.views.event_detail import event_detail
from core.views.post_detail import post_detail
from core.views.event_checkin import generate_qr_token, event_qr_checkin

app_name = 'core'

urlpatterns = [
    # --- General & Discovery ---
    path('', feed, name='home'),
    path('feed/', feed, name='feed'),
    path('directory/', directory, name='directory'),
    path('calendar/', calendar, name='calendar'),
    path('my-events/', my_events, name='my_events'),
    path('event/<int:event_id>/', event_detail, name='event_detail'),
    path('event/post/<int:post_id>/', event_detail, name='event_detail_by_post'),
    path('post/<int:post_id>/', post_detail, name='post_detail'),
    
    # --- Location & Institutional Discovery ---
    path('state/<int:state_id>/universities/', universities, name='universities'),
    path('state/<int:state_id>/universities/<int:university_id>/clubs/', clubs, name='clubs'),

    # --- Authentication ---
    path('signup/', sign_up, name='signup'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='core:feed'), name='logout'),

    # --- User Profile & Dashboards ---
    path('profile/', user_profile, name='profile'),
    path('profile/edit/', edit_profile, name='edit_profile'),
    path('student/dashboard/', student_dashboard, name='student_dashboard'),
    path('dashboard/', student_dashboard, name='dashboard_shortcut'),
    path('profile/manager/<int:club_id>/', manager_dashboard, name='manager_dashboard'),

    # --- Platform Admin Site ---
    path('admin-site/dashboard/', admin_dashboard_home, name='admin_dashboard'),
    path('admin-site/dashboard/queue/', admin_dashboard_task_queue, name='admin_task_queue'),
    path('admin-site/dashboard/task-status/', admin_dashboard_task_status, name='admin_task_status'),
    path('admin-site/dashboard/action/', admin_dashboard_action, name='admin_action'),
    
    # --- Caption Processing Workflow ---
    # Step 1: Temporal Classification
    path('admin-site/classification/temporal/', ac.admin_temporal_classification_dashboard, name='admin_temporal_classification_step1'),
    path('admin-site/classification/temporal/post/<int:post_id>/', ac.admin_classify_post_temporal, name='admin_classify_post_temporal_step1'),
    path('admin-site/classification/temporal/post/<int:post_id>/update/', ac.admin_update_post_event_status, name='admin_update_post_event_status_step1'),
    path('admin-site/classification/temporal/bulk/', ac.admin_bulk_temporal_classify, name='admin_bulk_temporal_classify_step1'),

    # Step 2: Event Classification
    path('admin-site/classification/event/', ac.admin_event_classification_dashboard, name='admin_event_classification_step2'),
    path('admin-site/classification/event/post/<int:post_id>/', ac.admin_classify_post_event, name='admin_classify_post_event_step2'),
    path('admin-site/classification/event/post/<int:post_id>/update/', ac.admin_update_post_event_category, name='admin_update_post_event_category_step2'),
    path('admin-site/classification/event/bulk/', ac.admin_bulk_event_classify, name='admin_bulk_event_classify_step2'),

    # Step 3: Date Extraction
    path('admin-site/classification/dates/', ac.admin_date_extraction_dashboard, name='admin_date_extraction_step3'),

    # Shared Bulk
    path('admin-site/classification/bulk/revert/', ac.admin_bulk_revert_classification, name='admin_bulk_revert_classification'),

    # --- Club Management & Profile ---
    path('club/<int:club_id>/', club_profile, name='club_profile'),
    path('club/<int:club_id>/join/', join_club, name='join_club'),
    path('club/<int:club_id>/apply-manager/', apply_manager, name='apply_manager'),
    path('club/<int:club_id>/admin/', club_admin_dashboard, name='club_admin_dashboard'),
    path('club/<int:club_id>/admin/<int:event_id>/', club_admin_dashboard, name='event_admin_dashboard'),
    path('club/<int:club_id>/create-event/', create_event, name='create_event'),
    path('club/<int:club_id>/event/<int:event_id>/edit/', edit_event, name='edit_event'),
    path('club/<int:club_id>/settings/', club_settings, name='club_settings'),
    path('membership/<int:membership_id>/<str:action>/', process_membership, name='process_membership'),

    # --- Event Operations & Attendance ---
    path('event/<int:event_id>/toggle-ready/<uuid:prereg_id>/', toggle_ready_status, name='toggle_ready_status'),
    path('event/<int:event_id>/toggle-attended/<uuid:prereg_id>/', toggle_attended_status, name='toggle_attended_status'),
    path('event/<int:event_id>/set-status/<str:status>/', set_event_status, name='set_event_status'),
    path('event/<int:event_id>/import-attendees/', import_attendees_csv, name='import_attendees_csv'),
    path('event/<int:event_id>/generate-qr-token/', generate_qr_token, name='generate_qr_token'),
    path('event/<int:event_id>/checkin/<str:token>/', event_qr_checkin, name='event_qr_checkin'),

    # --- Certificate Engine ---
    path('upload-certificate-template/<int:event_id>/', upload_certificate_template, name='upload_certificate_template'),
    path('event/<int:event_id>/download-certificates/', download_certificates, name='download_certificates'),
    path('event/<int:event_id>/download-certificate/', download_my_certificate, name='download_my_certificate'),

    # --- Password Reset Flow ---
    path('password-reset/', 
         auth_views.PasswordResetView.as_view(
             template_name='password_reset.html',
             success_url='/password-reset/done/',
             email_template_name='password_reset_email.html'
         ), 
         name='password_reset'),
    # "Success" page 
    path('password-reset/done/', 
         auth_views.PasswordResetDoneView.as_view(template_name='password_reset_done.html'), 
         name='password_reset_done'),

    # The link users click in their email
    path('password-reset-confirm/<uidb64>/<token>/', 
         auth_views.PasswordResetConfirmView.as_view(
             template_name='password_reset_confirm.html',
             success_url='/password-reset-complete/'
         ), 
         name='password_reset_confirm'),
    # Complete page after they successfully reset
    path('password-reset-complete/', 
         auth_views.PasswordResetCompleteView.as_view(template_name='password_reset_complete.html'), 
         name='password_reset_complete'),

    # --- Account Activation Flow ---
    path('activate/<uidb64>/<token>/', activate_account, name='activate'),
]
