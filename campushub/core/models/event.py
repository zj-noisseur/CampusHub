from django.db import models
from .post import Post

class Event(models.Model):
    post = models.OneToOneField(Post, on_delete=models.CASCADE, related_name='events')
    title = models.CharField(max_length=255)
    event_date = models.DateField()
    location = models.CharField(max_length=255)

    def __str__(self):
        return self.title