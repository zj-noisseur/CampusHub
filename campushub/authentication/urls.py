from django.urls import path
from . import views 

urlpatterns = [
    path('', views.register_student, name='home'),
    path('register/', views.register_student, name='register'),
    path('claim/', views.claim_club, name='claim_club'),
]