from django.db import models

class Institution(models.Model):
    university_name = models.CharField(max_length=255, unique=True)
    state = models.CharField(max_length=255)

    def __str__(self):
        return self.university_name