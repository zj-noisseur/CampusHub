from django.urls import path
from core.views.states import states
from core.views.clubs import clubs
from core.views.universities import universities

app_name = 'core'
urlpatterns = [
    path('', states, name='states'),
    path('state/<int:state_id>/universities/', universities, name='universities'),
    path('state/<int:state_id>/universities/<int:university_id>/clubs/', clubs, name='clubs')
]