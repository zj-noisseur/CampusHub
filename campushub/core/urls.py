from django.urls import path
from . import views # THIS is where the views import belongs!

urlpatterns = [
    
    # The upgraded ZIP download button
    path('my-certificates/', views.student_dashboard, name='student_dashboard'),

    path('dashboard/admin/', views.club_admin_dashboard, name='club_admin_dashboard'),
    path('import-csv/<int:event_id>/', views.import_attendees_csv, name='import_csv'),
    path('download-certificates/<int:event_id>/', views.download_certificates, name='download_certificates'),
]