from django.contrib import admin
from .models import ClubClaim, EventCertificate, Institution, Membership, PreRegisteredAttendee
from .models import User
from .models import State
from .models import Club
from .models import Committee
from .models import Post
from .models import Event
from .models import Attendance


class ClubAdmin(admin.ModelAdmin):
    list_display = ('name', 'institution', 'ig_handle')
    list_filter = ('institution', ('ig_handle', admin.EmptyFieldListFilter),
)
    
class InstitutionAdmin(admin.ModelAdmin):
    list_display = ('university_name', 'state')
    list_filter = ('state',)

    
admin.site.register(Institution, InstitutionAdmin)
admin.site.register(State)
admin.site.register(Club, ClubAdmin)
admin.site.register(User)
admin.site.register(Committee)
admin.site.register(Post)
admin.site.register(Event)
admin.site.register(ClubClaim)
admin.site.register(Attendance)
admin.site.register(Membership)
admin.site.register(PreRegisteredAttendee)
admin.site.register(EventCertificate)