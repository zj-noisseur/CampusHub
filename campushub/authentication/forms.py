from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser

class StudentRegistrationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        # These are the exact fields the student will fill out
        fields = ('email', 'student_name')