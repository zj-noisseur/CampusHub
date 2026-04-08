from django.db import models
from .club import Club

class Post(models.Model):
    club = models.ForeignKey(Club, on_delete=models.CASCADE, related_name='posts')
    ig_id = models.CharField(max_length=255, unique=True)
    short_code = models.CharField(max_length=100)
    caption = models.TextField(blank=True)
    timestamp = models.DateTimeField()

    def __str__(self):
        return self.short_code