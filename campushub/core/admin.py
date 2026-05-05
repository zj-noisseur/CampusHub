from django.contrib import admin

from .models import (
    Attendance,
    ClaimRequest,
    Club,
    ClubManager,
    Event,
    EventCertificate,
    Institution,
    Membership,
    Post,
    State,
    User,
)


class ClubAdmin(admin.ModelAdmin):
    list_display = ('name', 'institution', 'ig_handle')
    list_filter = ('institution', 'ig_handle')


class InstitutionAdmin(admin.ModelAdmin):
    list_display = ('university_name', 'state')
    list_filter = ('state',)


admin.site.register(Institution, InstitutionAdmin)
admin.site.register(State)
admin.site.register(Club, ClubAdmin)
admin.site.register(User)
admin.site.register(ClubManager)
admin.site.register(Post)
admin.site.register(Event)
admin.site.register(Attendance)
admin.site.register(Membership)
admin.site.register(EventCertificate)


@admin.register(ClaimRequest)
class ClaimRequestAdmin(admin.ModelAdmin):
    list_display = ('user', 'club', 'status')

    def save_model(self, request, obj, form, change):
        if change and obj.status == 'APPROVED':
            obj.club.is_claimed = True
            obj.club.save()

            ClubManager.objects.get_or_create(user=obj.user, club=obj.club)

            if not obj.user.is_staff:
                obj.user.is_staff = True
                obj.user.save()

        super().save_model(request, obj, form, change)
