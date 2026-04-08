from django.contrib import admin
from .models import Club, Institution, EventCertificate, Event, Post, Attendance, User, Committee, ClubClaim, Membership, PreRegisteredAttendee

# Register your models here.
admin.site.register(Institution)
admin.site.register(Club)
admin.site.register(User)
admin.site.register(Committee)
admin.site.register(Post)
admin.site.register(Event)
admin.site.register(ClubClaim)
admin.site.register(Attendance)
admin.site.register(Membership)
admin.site.register(PreRegisteredAttendee)
admin.site.register(EventCertificate)