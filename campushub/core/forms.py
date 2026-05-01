from django.contrib.auth.forms import UserCreationForm
from django import forms
from .models import User, Club, ClubManager, ClaimRequest, Membership

class StudentRegistrationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        # These are the exact fields the student will fill out
        fields = ('email', 'student_name','student_id', 'phone_number')
        widgets = {
            'email': forms.EmailInput(attrs={
                'class': 'input input-bordered w-full rounded-xl', 
                'placeholder': 'name@student.mmu.edu.my'
            }),
            'student_name': forms.TextInput(attrs={
                'class': 'input input-bordered w-full rounded-xl', 
                'placeholder': 'Your Full Name'
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

class MembershipApplicationForm(forms.ModelForm):
    student_name = forms.CharField(disabled=True, required=False, widget=forms.TextInput(attrs={'class': 'input input-bordered w-full rounded-xl bg-gray-100'}))
    student_id = forms.CharField(max_length=20, required=True, widget=forms.TextInput(attrs={'class': 'input input-bordered w-full rounded-xl', 'placeholder': 'e.g., 1234567890'}))
    phone_number = forms.CharField(max_length=20, required=True, widget=forms.TextInput(attrs={'class': 'input input-bordered w-full rounded-xl', 'placeholder': 'e.g., 012-3456789'}))
    
    class Meta:
        model = Membership
        # Assuming your model has these fields based on your previous design
        fields = ['club', 'payment_proof']
        
        widgets = {
            'club': forms.Select(attrs={
                'class': 'select select-bordered w-full rounded-xl',
            }),
            'membership_type': forms.Select(attrs={
                'class': 'select select-bordered w-full rounded-xl',
                'id': 'membership-type-select' # We need this ID for our JavaScript magic later!
            }),
            'payment_proof': forms.ClearableFileInput(attrs={
                'class': 'file-input file-input-bordered w-full rounded-xl',
                'accept': '.pdf,.jpg,.jpeg,.png',
                'id': 'receipt-upload'
            }),
        }
