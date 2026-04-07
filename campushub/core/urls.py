from django.urls import path
from . import views # THIS is where the views import belongs!

urlpatterns = [
    # Any other paths your teammate made might be here
    
    # Your certificate test path
    path('test-certificate/', views.test_certificate, name='test_certificate'),
]