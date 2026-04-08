from django.contrib import admin
from .models import ClubClaim, EventCertificate, Institution, Membership, PreRegisteredAttendee
from .models import User
from .models import Club
from .models import Committee
from .models import Post
from .models import Event
from .models import Attendance

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