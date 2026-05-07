from django.urls import path
from .views import certificates, imports, clubs, dashboards

app_name = 'core'
urlpatterns = [
    # Club Profile and Admin
    path('club/<int:club_id>/', dashboards.club_profile, name='club_profile'),
    path('club/<int:club_id>/admin/', dashboards.club_admin_dashboard, name='club_admin_dashboard'),
    path('club/<int:club_id>/admin/<int:event_id>/', dashboards.club_admin_dashboard, name='event_admin_dashboard'),
    path('club/<int:club_id>/create-event/', dashboards.create_event, name='create_event'),
    path('club/<int:club_id>/settings/', dashboards.club_settings, name='club_settings'),
    
    # Student Dashboard
    path('student/dashboard/', dashboards.student_dashboard, name='student_dashboard'),
    path('dashboard/', dashboards.student_dashboard, name='dashboard_shortcut'),
    
    # Event Actions
    path('event/<int:event_id>/toggle-ready/<uuid:prereg_id>/', dashboards.toggle_ready_status, name='toggle_ready_status'),
    path('event/<int:event_id>/toggle-attended/<uuid:prereg_id>/', dashboards.toggle_attended_status, name='toggle_attended_status'),
    path('event/<int:event_id>/set-status/<str:status>/', dashboards.set_event_status, name='set_event_status'),
    path('event/<int:event_id>/import-attendees/', imports.import_attendees_csv, name='import_attendees_csv'),
    
    # Certificates
    path('upload-certificate-template/<int:event_id>/', certificates.upload_certificate_template, name='upload_certificate_template'),
    path('event/<int:event_id>/download-certificates/', certificates.download_certificates, name='download_certificates'),
    path('event/<int:event_id>/download-certificate/', certificates.download_my_certificate, name='download_my_certificate'),
    
    # Universities and Clubs (using the clubs view)
    path('state/<int:state_id>/universities/<int:university_id>/clubs/', clubs.clubs, name='clubs'),
]
