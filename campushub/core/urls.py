from django.urls import path
from .views import dashboards, certificates, imports, clubs

app_name = 'core'
urlpatterns = [
    #Choose a club
    path('my-clubs/', clubs.club_profile, name='club_profile'),

    #The Event List
    path('club/<int:club_id>/dashboard/', dashboards.club_admin_dashboard, name='club_admin_dashboard'),

    # The Core Features you want to show
    path('import-csv/<int:event_id>/', imports.import_attendees_csv, name='import_csv'),
    path('download-certificates/<int:event_id>/', certificates.download_certificates, name='download_certificates'),

    #button to mark as ready and attanded
    path('event/<int:event_id>/toggle-ready/<str:prereg_id>/', dashboards.toggle_ready_status, name='toggle_ready'),
    path('event/<int:event_id>/toggle-attended/<str:prereg_id>/', dashboards.toggle_attended_status, name='toggle_attended'),
]