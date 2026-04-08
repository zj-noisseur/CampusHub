from django.contrib import admin
from .models import Institution
from .models import User
from .models import Club
from .models import Committee
from .models import Post
from .models import Event

admin.site.register(Institution)
admin.site.register(Club)
admin.site.register(User)
admin.site.register(Committee)
admin.site.register(Post)
admin.site.register(Event)
