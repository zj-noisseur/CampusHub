from django.db import models
from .user import User
from .event import Event

class Attendance(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='attendance_records')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    guest_name = models.CharField(max_length=255, blank=True)
    scanned_at = models.DateTimeField(auto_now_add=True)