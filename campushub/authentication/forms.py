from django.contrib.auth.forms import UserCreationForm
from .models import User
from django import forms

class StudentRegistrationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        # These are the exact fields the student will fill out
        fields = ('email', 'student_name')
        widgets = {
            'email': forms.EmailInput(attrs={
                'class': 'input input-bordered w-full rounded-xl', 
                'placeholder': 'name@student.mmu.edu.my'
            }),
            'student_name': forms.TextInput(attrs={
                'class': 'input input-bordered w-full rounded-xl', 
                'placeholder': 'John Doe'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Django automatically generates two password fields for safety.
        # This loop applies the beautiful styling to both of them dynamically!
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'input input-bordered w-full rounded-xl'})