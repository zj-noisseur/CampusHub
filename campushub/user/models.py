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
