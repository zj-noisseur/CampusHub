from django.contrib import admin
from .models import User, Club, ClubManager, ClaimRequest, Membership

# Register your models here.
admin.site.register(User)
admin.site.register(Club)
admin.site.register(ClubManager)
admin.site.register(ClaimRequest)
admin.site.register(Membership)