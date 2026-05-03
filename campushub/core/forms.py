from django.contrib.auth.forms import UserCreationForm, get_user_model
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

User = get_user_model()

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        # Only list the fields they are allowed to change!
        fields = ['student_name', 'bio','profile_picture', 'faculty', 'major', 'year_of_study']

        widgets = {'student_name': forms.TextInput(attrs={'class': 'input input-bordered w-full rounded-xl'}),
            'bio': forms.Textarea(attrs={'class': 'textarea textarea-bordered w-full rounded-xl', 'rows': 4}),
            'profile_picture': forms.FileInput(attrs={'class': 'file-input file-input-bordered w-full rounded-xl'}),
            
            'faculty': forms.Select(attrs={'class': 'select select-bordered w-full rounded-xl'}),
            'major': forms.TextInput(attrs={'class': 'input input-bordered w-full rounded-xl', 'placeholder': 'e.g., Software Engineering'}),
            'year_of_study': forms.Select(attrs={'class': 'select select-bordered w-full rounded-xl'}),
        }
        
        # Optional: Add help text so they know what alt_email is for
        help_texts = {
            'alt_email': 'Add a personal email (like Gmail) so you can log in if you lose access to your student email.',
        }

class ClubSettingsForm(forms.ModelForm):
    class Meta:
        model = Club
        # These are all the fields a manager should be allowed to edit!
        fields = [
            'description', 
            'logo', 
            'banner', 
            'social_instagram', 
            'social_linkedin', 
            'social_twitter', 
            'social_facebook', 
            'social_discord', 
            'social_website',
            'membership_fee',
            'payment_qr_code',
        ]
        
        # Adding some basic DaisyUI/Tailwind styling to the inputs
        widgets = {
            'description': forms.Textarea(attrs={'class': 'textarea textarea-bordered w-full', 'rows': 4, 'placeholder': 'Describe your club...'}),
            'logo': forms.FileInput(attrs={'class': 'file-input file-input-bordered w-full max-w-xs'}),
            'banner': forms.FileInput(attrs={'class': 'file-input file-input-bordered w-full max-w-xs'}),
            'social_instagram': forms.URLInput(attrs={'class': 'input input-bordered w-full', 'placeholder': 'https://instagram.com/...'}),
            'social_linkedin': forms.URLInput(attrs={'class': 'input input-bordered w-full', 'placeholder': 'https://linkedin.com/...'}),
            'social_twitter': forms.URLInput(attrs={'class': 'input input-bordered w-full', 'placeholder': 'https://twitter.com/...'}),
            'social_facebook': forms.URLInput(attrs={'class': 'input input-bordered w-full', 'placeholder': 'https://facebook.com/...'}),
            'social_discord': forms.URLInput(attrs={'class': 'input input-bordered w-full', 'placeholder': 'https://discord.gg/...'}),
            'social_website': forms.URLInput(attrs={'class': 'input input-bordered w-full', 'placeholder': 'https://...'}),
            'membership_fee': forms.NumberInput(attrs={'class': 'input input-bordered w-full max-w-xs', 'step': '0.01'}),
            'payment_qr_code': forms.FileInput(attrs={'class': 'file-input file-input-bordered w-full max-w-xs'}),
        }