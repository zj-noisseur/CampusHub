import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True, help_text="Please provide your student email address. A confirmation email will be sent for the purpose of activating your account.")
    student_id = models.CharField(max_length=10, unique=True, help_text="Please provide your student ID.")
    
    def __str__(self):
        return f"{self.username} ({self.student_id})"