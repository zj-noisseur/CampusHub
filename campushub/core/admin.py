from django.contrib import admin
from .models import NewClubRequest

from core.models import (
    Attendance,
    ClaimRequest,
    Club,
    ClubManager,
    ClubScrapeStatus,
    Event,
    EventCertificate,
    Institution,
    Membership,
    Post,
    PreRegisteredAttendee,
    State,
    User,
)

# --- Location & Institutional Admins ---
class InstitutionAdmin(admin.ModelAdmin):
    list_display = ('university_name', 'state')
    list_filter = ('state',)

admin.site.register(State)
admin.site.register(Institution, InstitutionAdmin)

# --- Club & Membership Admins ---
class ClubAdmin(admin.ModelAdmin):
    list_display = ('name', 'institution', 'club_category', 'ig_handle')
    list_filter = ('institution', 'club_category')

admin.site.register(Club, ClubAdmin)
admin.site.register(ClubManager)
@admin.register(Membership)
class MembershipAdmin(admin.ModelAdmin):
    list_display = ('user', 'club', 'membership_type', 'status', 'joined_at')
    list_filter = ('status', 'membership_type', 'club')
    search_fields = ('user__student_name', 'user__email', 'club__name')
    readonly_fields = ('joined_at',)

# --- Post & Event Admins ---
admin.site.register(Post)
@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'club', 'event_date', 'status', 'join_mode')
    list_filter = ('status', 'join_mode', 'club')
    raw_id_fields = ('club',)
    search_fields = ('title', 'club__name')
admin.site.register(Attendance)

class PreRegisteredAttendeeAdmin(admin.ModelAdmin):
    list_display = ('event', 'user', 'guest_name', 'guest_email', 'is_attended', 'created_at')
    list_filter = ('event', 'is_attended')
    search_fields = ('guest_name', 'guest_email', 'user__student_name')

admin.site.register(PreRegisteredAttendee, PreRegisteredAttendeeAdmin)
admin.site.register(EventCertificate)
admin.site.register(ClubScrapeStatus)

# --- User & Claiming Admins ---
admin.site.register(User)

@admin.register(ClaimRequest)
class ClaimRequestAdmin(admin.ModelAdmin):
    list_display = ('user', 'club', 'status', 'claimer_designation', 'submitted_at')
    list_filter = ('status',)

    def save_model(self, request, obj, form, change):
        if change and obj.status == 'APPROVED':
            # Mark the club as claimed
            obj.club.is_claimed = True
            obj.club.save()

            # Create the manager entry with ROOT role and the chosen designation
            ClubManager.objects.get_or_create(
                user=obj.user, 
                club=obj.club,
                defaults={
                    'role': 'ROOT',
                    'designation': obj.claimer_designation
                }
            )

            # Ensure the user has staff access to the admin panel
            if not obj.user.is_staff:
                obj.user.is_staff = True
                obj.user.save()

        super().save_model(request, obj, form, change)

@admin.register(NewClubRequest)
class NewClubRequestAdmin(admin.ModelAdmin):
    list_display = ('club_name', 'institution', 'requester', 'status', 'submitted_at')
    list_filter = ('status', 'institution', 'category')
    search_fields = ('club_name', 'requester__student_name', 'requester__email')
    readonly_fields = ('submitted_at',)