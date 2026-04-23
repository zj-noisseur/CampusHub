from django.contrib import admin
from .models import User, Club, ClubManager, ClaimRequest, Membership
# Register your models here.


# Register your models here.
admin.site.register(User)
admin.site.register(Club)
admin.site.register(ClubManager)
admin.site.register(Membership)

@admin.register(ClaimRequest)
class ClaimRequestAdmin(admin.ModelAdmin):
    list_display = ('user', 'club', 'status') 

    def save_model(self, request, obj, form, change):
        # 'change' is True if we are updating an existing request (not creating a new one)
        if change:
            # Check if the admin just approved it!
            if obj.status == 'APPROVED':
                
                # 1. Mark the Club as claimed so no one else can claim it
                obj.club.is_claimed = True
                obj.club.save()

                # 2. Automatically create the ClubManager profile
                # get_or_create prevents crashing if they are already a manager
                ClubManager.objects.get_or_create(
                    user=obj.user,
                    club=obj.club
                )

                # 3.Give the student 'staff' status so they can actually log into the admin dashboard!
                if not obj.user.is_staff:
                    obj.user.is_staff = True
                    obj.user.save()

        if obj.status == 'REJECTED':
            pass


        super().save_model(request, obj, form, change)