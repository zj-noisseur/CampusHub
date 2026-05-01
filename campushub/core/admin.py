from django.contrib import admin
from .models import Club, Institution, EventCertificate, Event, Post, Attendance, User, ClubManager, ClaimRequest, Membership, PreRegisteredAttendee

# Register your models here.
admin.site.register(Institution)
admin.site.register(Club)
admin.site.register(User)
admin.site.register(ClubManager)
admin.site.register(Post)
admin.site.register(Event)
admin.site.register(ClaimRequest)
admin.site.register(Attendance)
admin.site.register(Membership)
admin.site.register(PreRegisteredAttendee)
admin.site.register(EventCertificate)