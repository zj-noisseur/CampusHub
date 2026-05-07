from core.views.dashboards import club_profile, club_admin_dashboard, club_settings, student_dashboard
from core.views.imports import import_attendees_csv
from core.views.certificates import download_certificates, download_my_certificate
from core.views.dashboards import toggle_ready_status, toggle_attended_status, set_event_status

__all__ = [
    'club_profile',
    'club_admin_dashboard',
    'club_settings',
    'student_dashboard',
    'import_attendees_csv',
    'download_certificates',
    'download_my_certificate',
    'toggle_ready_status',
    'toggle_attended_status',
    'set_event_status',
]
