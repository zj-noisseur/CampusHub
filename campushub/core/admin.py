from django.contrib import admin
from .models import Club, Institution, EventCertificate, Event, Post, Attendance, User, ClubManager, ClaimRequest, Membership, PreRegisteredAttendee

# Register your models here.
admin.site.register(Institution)
admin.site.register(Club)
admin.site.register(User)
admin.site.register(ClubManager)
admin.site.register(Post)
admin.site.register(Event)

@admin.register(ClaimRequest)
class ClaimRequestAdmin(admin.ModelAdmin):
    list_display = ('user', 'club', 'status')

    def save_model(self, request, obj, form, change):
        if change: 
            if obj.status == 'APPROVED':
                obj.club.is_claimed = True
                obj.club.save()

                ClubManager.objects.get_or_create(user=obj.user, club=obj.club)

                if not obj.user.is_staff:
                    obj.user.is_staff = True
                    obj.user.save()
        if obj.status =='REJECTED':
            pass

        super().save_model(request, obj, form, change)

admin.site.register(Attendance)
admin.site.register(Membership)
admin.site.register(PreRegisteredAttendee)
admin.site.register(EventCertificate)