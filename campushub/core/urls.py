from django.urls import path
from . import views 
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.sign_up, name='home'),
    path('sign_up/', views.sign_up, name='sign_up'),
    path('claim/', views.claim_club, name='claim_club'),
    path('login/', auth_views.LoginView.as_view(template_name='core/login.html'), name='login'),
    path('profile/', views.user_profile, name='profile'),
    path('dashboard/', views.manager_dashboard, name='manager_dashboard'),
    path('dashboard/member/<int:membership_id>/<str:action>/', views.process_membership, name='process_membership'),
]