from django.urls import path
from . import views 
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.sign_up, name='home'),
    path('signup/', views.sign_up, name='sign_up'),
    path('claim/', views.claim_club, name='claim_club'),
    path('profile/', views.user_profile, name='profile'),
    path('login/', auth_views.LoginView.as_view(template_name='core/login.html'), name='login'),
]