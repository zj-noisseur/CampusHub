from django.db import models 
from django.conf import settings

class PreRegisteredAttendee(models.Model):
    event = models.ForeignKey('feed.Event', on_delete=models.CASCADE, related_name='pre_registered')
    
    email = models.EmailField(max_length=255)
    name = models.CharField(max_length=255, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('event', 'email')

    def __str__(self):
        return f"{self.name or self.email} - {self.event.title}"


class EventCertificate(models.Model):
    event = models.ForeignKey('feed.Event', on_delete=models.CASCADE, related_name='certificates')
    
    template_image = models.ImageField(upload_to='certificate_templates/')
    
    name_center_x = models.IntegerField()
    name_center_y = models.IntegerField()
    font_size = models.IntegerField(default=24)
    font_color = models.CharField(max_length=7, default='#000000') 
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Certificate Template for {self.event.title}"
    
    
class Attendance(models.Model):
    event = models.ForeignKey('feed.Event', on_delete=models.CASCADE, related_name='attendances')
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    
    guest_name = models.CharField(max_length=255, null=True, blank=True)
    guest_email = models.EmailField(max_length=255, null=True, blank=True)
    guest_phone = models.CharField(max_length=50, null=True, blank=True)
    
    check_in_time = models.DateTimeField(auto_now_add=True)
    certificate_sent = models.BooleanField(default=False)

    def __str__(self):
        attendee_name = self.user.username if self.user else self.guest_name
        return f"{attendee_name} - {self.event.title}"