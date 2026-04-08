from django.urls import path
from . import views

app_name = 'core'
urlpatterns = [
    #dashboard list
    path('dashboard/admin/', views.club_admin_dashboard, name='club_admin_dashboard'),
    path('dashboard/student/', views.student_dashboard, name='student_dashboard'),
    
    #clubadmin tool
    path('import-csv/<int:event_id>/', views.import_attendees_csv, name='import_csv'),
    path('download-certificates/<int:event_id>/', views.download_certificates, name='download_certificates'),
    
    #student tool
    path('download-my-certificate/<uuid:attendance_id>/', views.download_my_certificate, name='download_my_certificate'),
]