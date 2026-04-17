from django.urls import path
from .views import dashboards, certificates, imports

app_name = 'core'
urlpatterns = [
    # Dashboards
    path('dashboard/admin/', dashboards.club_admin_dashboard, name='club_admin_dashboard'),
    path('dashboard/student/', dashboards.student_dashboard, name='student_dashboard'),
    
    # Imports
    path('import-csv/<int:event_id>/', imports.import_attendees_csv, name='import_csv'),
    
    # Certificates
    path('download-certificates/<int:event_id>/', certificates.download_certificates, name='download_certificates'),
    path('download-my-certificate/<uuid:attendance_id>/', certificates.download_my_certificate, name='download_my_certificate'),
]