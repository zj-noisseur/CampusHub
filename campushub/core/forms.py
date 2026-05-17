from django.contrib.auth.forms import UserCreationForm, get_user_model
from django import forms
from core.models import Club, ClubManager, ClaimRequest, Membership, Event, EventCertificate

User = get_user_model()

class StudentRegistrationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('student_name', 'email')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['student_name'].widget.attrs.update({
            'class': 'input input-bordered w-full rounded-xl',
            'placeholder': 'John Doe'
        })
        self.fields['email'].widget.attrs.update({
            'class': 'input input-bordered w-full rounded-xl',
            'placeholder': 'student@mmu.edu.my'
        })

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            email = email.lower()
            if User.objects.filter(email=email).exists():
                raise forms.ValidationError("An account with this email address already exists.")
        return email


class ClubClaimForm(forms.ModelForm):
    proof_document = forms.FileField(
        required=True,
        widget=forms.FileInput(attrs={
            'class': 'file-input file-input-bordered w-full rounded-xl',
            'accept': '.pdf,.doc,.docx,.jpg,.jpeg,.png'
        }),
        help_text="Upload official letters, SSM certificates, or student union registration documents."
    )

    class Meta:
        model = ClaimRequest
        fields = ['club', 'proof_document', 'claimer_designation']
        widgets = {
            'club': forms.Select(attrs={
                'class': 'select select-bordered w-full rounded-xl',
            }),
            'claimer_designation': forms.TextInput(attrs={
                'class': 'input input-bordered w-full rounded-xl',
                'placeholder': 'e.g., Club President, Secretary'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['club'].queryset = Club.objects.filter(is_claimed=False)

ClaimClubForm = ClubClaimForm


class MembershipApplicationForm(forms.ModelForm):
    student_name = forms.CharField(disabled=True, required=False, widget=forms.TextInput(attrs={'class': 'input input-bordered w-full rounded-xl bg-gray-100'}))
    student_id = forms.CharField(max_length=20, required=True, widget=forms.TextInput(attrs={'class': 'input input-bordered w-full rounded-xl', 'placeholder': 'e.g., 1234567890'}))
    phone_number = forms.CharField(max_length=20, required=True, widget=forms.TextInput(attrs={'class': 'input input-bordered w-full rounded-xl', 'placeholder': 'e.g., 012-3456789'}))

    class Meta:
        model = Membership
        fields = ['club', 'payment_proof']
        widgets = {
            'club': forms.Select(attrs={
                'class': 'select select-bordered w-full rounded-xl',
            }),
            'membership_type': forms.Select(attrs={
                'class': 'select select-bordered w-full rounded-xl',
                'id': 'membership-type-select'
            }),
            'payment_proof': forms.ClearableFileInput(attrs={
                'class': 'file-input file-input-bordered w-full rounded-xl',
                'accept': '.pdf,.jpg,.jpeg,.png',
                'id': 'receipt-upload'
            }),
        }


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['student_name', 'bio', 'profile_picture', 'faculty', 'major', 'year_of_study']
        widgets = {
            'student_name': forms.TextInput(attrs={'class': 'input input-bordered w-full rounded-xl'}),
            'bio': forms.Textarea(attrs={'class': 'textarea textarea-bordered w-full rounded-xl', 'rows': 4}),
            'profile_picture': forms.FileInput(attrs={'class': 'file-input file-input-bordered w-full rounded-xl'}),
            'faculty': forms.Select(attrs={'class': 'select select-bordered w-full rounded-xl'}),
            'major': forms.TextInput(attrs={'class': 'input input-bordered w-full rounded-xl', 'placeholder': 'e.g., Software Engineering'}),
            'year_of_study': forms.Select(attrs={'class': 'select select-bordered w-full rounded-xl'}),
        }
        help_texts = {
            'alt_email': 'Add a personal email (like Gmail) so you can log in if you lose access to your student email.',
        }


class ClubSettingsForm(forms.ModelForm):
    class Meta:
        model = Club
        fields = [
            'club_category',
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
            'renewal_policy',
        ]
        widgets = {
            'club_category': forms.Select(attrs={'class': 'select select-bordered w-full'}),
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
            'renewal_policy': forms.Select(attrs={'class': 'select select-bordered w-full max-w-xs'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        social_fields = [
            'social_instagram', 'social_linkedin', 'social_twitter', 
            'social_facebook', 'social_discord', 'social_website'
        ]
        
        for field in social_fields:
            value = cleaned_data.get(field)
            if value and not value.startswith(('http://', 'https://')):
                cleaned_data[field] = 'https://' + value
        
        return cleaned_data


class EventCreationForm(forms.ModelForm):
    banner_image = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={'class': 'file-input file-input-bordered w-full'}),
        help_text="Upload a specific banner or image for this event."
    )
    
    class Meta:
        model = Event
        fields = ['title', 'event_date', 'location']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'input input-bordered w-full', 'placeholder': 'e.g., Annual Tech Symposium'}),
            'event_date': forms.DateInput(attrs={'class': 'input input-bordered w-full', 'type': 'date'}),
            'location': forms.TextInput(attrs={'class': 'input input-bordered w-full', 'placeholder': 'e.g., Main Hall'}),
        }


class CertificateUploadForm(forms.ModelForm):
    class Meta:
        model = EventCertificate
        fields = ['template_image', 'name_center_x', 'name_center_y', 'font_color', 'font_size', 'font_name', 'custom_text', 'custom_x', 'custom_y', 'custom_font_color', 'custom_font_size']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # If we are updating an existing certificate, the image is not strictly required 
        # (it will keep the old one if not provided).
        if self.instance and self.instance.pk:
            self.fields['template_image'].required = False
