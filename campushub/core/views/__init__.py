from core.views.sign_up import sign_up
from core.views.claim_club import claim_club
from core.views.profile import user_profile
from core.views.manager_dashboard import manager_dashboard, process_membership, update_club_settings
from core.views.profile import edit_profile
from core.views.dashboards import club_profile, club_admin_dashboard, club_settings, student_dashboard
from core.views.imports import import_attendees_csv
from core.views.certificates import download_certificates, download_my_certificate
from core.views.dashboards import toggle_ready_status, toggle_attended_status, set_event_status
from core.views.club_actions import join_club, apply_manager

__all__ = [
    'sign_up',
    'claim_club',
    'user_profile',
    'manager_dashboard',
    'process_membership',
    'update_club_settings',
    'edit_profile',
    'club_profile',
    'club_admin_dashboard',
    'club_settings',
    'student_dashboard',
    'import_attendees_csv',
    'download_certificates',
    'download_my_certificate',
    'join_club',
    'apply_manager',
    'toggle_ready_status',
    'toggle_attended_status',
    'set_event_status',
]
