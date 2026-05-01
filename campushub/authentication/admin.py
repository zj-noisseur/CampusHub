from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import CustomUser, Club, ClubManager, ClaimRequest, Membership

admin.site.register(CustomUser)
admin.site.register(Club)
admin.site.register(ClubManager)
admin.site.register(ClaimRequest)
admin.site.register(Membership)