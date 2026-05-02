from django.urls import path
from .views import certificates, imports, clubs, dashboards

app_name = 'core'
urlpatterns = [
    #Choose a club

    #The Dashboard List
    path('club/<int:club_id>/', dashboards.club_profile, name='club_profile'),
    path('club/<int:club_id>/dashboard/', dashboards.club_admin_dashboard, name='club_admin_dashboard'),
    path('club/<int:club_id>/settings/', dashboards.club_settings, name='club_settings'),
    path('club/<int:club_id>/event/<int:event_id>/', dashboards.club_admin_dashboard, name='event_admin_dashboard'),
    path('club/<int:club_id>/event/create/', dashboards.create_event, name='create_event'),
    path('dashboard/', dashboards.student_dashboard, name='student_dashboard'),

    # The Core Features you want to show
    path('import-csv/<int:event_id>/', imports.import_attendees_csv, name='import_csv'),
    path('download-certificates/<int:event_id>/', certificates.download_certificates, name='download_certificates'),
    path('download-my-certificate/<int:event_id>/', certificates.download_my_certificate, name='download_my_certificate'),

    #button to mark as ready and attanded
    path('event/<int:event_id>/toggle-ready/<str:prereg_id>/', dashboards.toggle_ready_status, name='toggle_ready'),
    path('event/<int:event_id>/toggle-attended/<str:prereg_id>/', dashboards.toggle_attended_status, name='toggle_attended'),

    path('event/<int:event_id>/set-status/<str:status>/', dashboards.set_event_status, name='set_event_status'),
]