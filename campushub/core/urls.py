from django.urls import path
from django.contrib.auth import views as auth_views
from core.views.directory import directory
from core.views.clubs import clubs
from core.views.universities import universities
from core.views.admin_dashboard import admin_dashboard_home, admin_dashboard_action, admin_dashboard_task_queue, admin_dashboard_task_status,admin_manager_requests, admin_approve_manager_claim, admin_reject_manager_claim
from core.views import admin_classification as ac
from core.views.feed import feed
from core.views.sign_up import sign_up, activate_account,resend_activation
from core.views.claim_club import claim_club
from core.views.profile import user_profile, edit_profile
from core.views.calendar import calendar
from core.views.club_actions import join_club, apply_manager
from core.views.manager_dashboard import import_members, manager_dashboard, process_membership, extend_club_validity, update_post_extracted_details, club_extract_post_details, club_revert_post_extraction, club_task_queue, club_classify_post_temporal, club_update_post_event_status, club_classify_post_event, club_update_post_event_category
from core.views.imports import import_attendees_csv
from core.views.certificates import upload_certificate_template, download_certificates, download_my_certificate
from core.views.dashboards import club_profile, club_admin_dashboard, club_settings, student_dashboard, toggle_ready_status, toggle_attended_status, set_event_status, create_event, edit_event, my_events, manage_attendee_status, trigger_club_scrape, manage_linked_posts
from core.views.event_detail import event_detail, join_event
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
    path('event/<int:event_id>/join/', join_event, name='join_event'),
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

    #--- Club Claiming ---
    path('admin-site/dashboard/manager-requests/', admin_manager_requests, name='admin_manager_requests'),
    path('admin-site/dashboard/manager-requests/<int:claim_id>/approve/', admin_approve_manager_claim, name='approve_manager_claim'),
    path('admin-site/dashboard/manager-requests/<int:claim_id>/reject/', admin_reject_manager_claim, name='reject_manager_claim'),
    
    
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

    # Step 3: Data Extraction
    path('admin-site/classification/data/', ac.admin_data_extraction_dashboard, name='admin_data_extraction_dashboard'),
    path('admin-site/classification/data/post/<int:post_id>/', ac.admin_extract_post_details, name='admin_extract_post_details'),
    path('admin-site/classification/data/post/<int:post_id>/revert/', ac.admin_revert_post_extraction, name='admin_revert_post_extraction'),
    path('admin-site/classification/data/bulk/', ac.admin_bulk_extract_details, name='admin_bulk_extract_details'),
    path('admin-site/classification/data/bulk/revert/', ac.admin_bulk_revert_extraction, name='admin_bulk_revert_extraction'),

    # Shared Bulk
    path('admin-site/classification/bulk/revert/', ac.admin_bulk_revert_classification, name='admin_bulk_revert_classification'),

    # --- Club Management & Profile ---
    path('club/<int:club_id>/', club_profile, name='club_profile'),
    path('club/<int:club_id>/join/', join_club, name='join_club'),
    path('club/<int:club_id>/apply-manager/', apply_manager, name='apply_manager'),
    path('club/<int:club_id>/admin/', club_admin_dashboard, name='club_admin_dashboard'),
    path('club/<int:club_id>/admin/<int:event_id>/', club_admin_dashboard, name='event_admin_dashboard'),
    path('club/<int:club_id>/admin/<int:event_id>/link-posts/', manage_linked_posts, name='manage_linked_posts'),
    path('club/<int:club_id>/create-event/', create_event, name='create_event'),
    path('club/<int:club_id>/event/<int:event_id>/edit/', edit_event, name='edit_event'),
    path('club/<int:club_id>/settings/', club_settings, name='club_settings'),
    path('club/<int:club_id>/scrape/', trigger_club_scrape, name='trigger_club_scrape'),
    path('membership/<int:membership_id>/<str:action>/', process_membership, name='process_membership'),
    path('club/<int:club_id>/extend-validity/', extend_club_validity, name='extend_club_validity'),
    path('club/<int:club_id>/post/<int:post_id>/update-extracted/', update_post_extracted_details, name='update_post_extracted_details'),
    path('club/<int:club_id>/post/<int:post_id>/extract/', club_extract_post_details, name='club_extract_post_details'),
    path('club/<int:club_id>/post/<int:post_id>/revert-extract/', club_revert_post_extraction, name='club_revert_post_extraction'),
    path('club/<int:club_id>/task-queue/', club_task_queue, name='club_task_queue'),
    path('club/<int:club_id>/post/<int:post_id>/classify-temporal/', club_classify_post_temporal, name='club_classify_post_temporal'),
    path('club/<int:club_id>/post/<int:post_id>/update-temporal/', club_update_post_event_status, name='club_update_post_event_status'),
    path('club/<int:club_id>/post/<int:post_id>/classify-event/', club_classify_post_event, name='club_classify_post_event'),
    path('club/<int:club_id>/post/<int:post_id>/update-event/', club_update_post_event_category, name='club_update_post_event_category'),
    path('club/<int:club_id>/import/', import_members, name='import_members'),

    # --- Event Operations & Attendance ---
    path('event/<int:event_id>/toggle-ready/<uuid:prereg_id>/', toggle_ready_status, name='toggle_ready_status'),
    path('event/<int:event_id>/toggle-attended/<uuid:prereg_id>/', toggle_attended_status, name='toggle_attended_status'),
    path('event/<int:event_id>/attendee/<uuid:prereg_id>/<str:action>/', manage_attendee_status, name='manage_attendee_status'),
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
             email_template_name='password_reset_email.html',
             html_email_template_name='password_reset_email.html'
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
    path('resend-activation/', resend_activation, name='resend_activation'),
]
