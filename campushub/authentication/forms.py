from django.contrib.auth.forms import UserCreationForm
from .models import User
from django import forms
from .models import User, Club, ClubManager, ClaimRequest, Membership

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

class ClaimClubForm(forms.ModelForm):
    class Meta:
        model = ClaimRequest
        fields = ['club', 'proof_document']
        
        # Apply DaisyUI styling specific to dropdowns and file uploads
        widgets = {
            'club': forms.Select(attrs={
                'class': 'select select-bordered w-full rounded-xl',
            }),
            'proof_document': forms.ClearableFileInput(attrs={
                'class': 'file-input file-input-bordered w-full rounded-xl',
                'accept': '.pdf,.jpg,.jpeg,.png' # Force them to upload valid document types
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # CRITICAL LOGIC: Only show clubs in the dropdown that are NOT claimed yet!
        self.fields['club'].queryset = Club.objects.filter(is_claimed=False)