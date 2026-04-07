from django.contrib import admin
from .models import Club, Institution, EventCertificate, Event, Post

admin.site.register(Institution)
admin.site.register(Club)
admin.site.register(Event)
admin.site.register(Post)
admin.site.register(EventCertificate) 
