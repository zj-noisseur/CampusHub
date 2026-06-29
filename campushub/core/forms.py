from django.contrib.auth.forms import UserCreationForm, get_user_model
from django import forms
from core.models import Club, ClubManager, ClaimRequest, Membership, Event, EventCertificate

User = get_user_model()

class StudentRegistrationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('student_name', 'email', 'student_id', 'phone_number')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Style standard fields with beautiful placeholders
        self.fields['student_name'].widget.attrs.update({
            'class': 'input input-bordered w-full rounded-xl',
            'placeholder': 'Your Full Name'
        })
        self.fields['email'].widget.attrs.update({
            'class': 'input input-bordered w-full rounded-xl',
            'placeholder': 'name@student.mmu.edu.my'
        })
        self.fields['student_id'].widget.attrs.update({
            'class': 'input input-bordered w-full rounded-xl',
            'placeholder': 'e.g., 1211102234'
        })
        self.fields['phone_number'].widget.attrs.update({
            'class': 'input input-bordered w-full rounded-xl',
            'placeholder': 'e.g., 012-3456789'
        })
        
        # Automatically style password fields as well
        for field_name in ['password1', 'password2']:
            if field_name in self.fields:
                self.fields[field_name].widget.attrs.update({
                    'class': 'input input-bordered w-full rounded-xl',
                    'placeholder': '••••••••'
                })

    def clean_email(self):
        email = self.cleaned_data.get('email')
        student_id = self.data.get('student_id') # Get ID from raw form data
        User = get_user_model()
        
        if email:
            email = email.lower()
            existing_user = User.objects.filter(email=email).first()
            
            if existing_user:
                # If this email already belongs to the exact ghost account we are waking up, forgive the error!
                if not existing_user.is_active and existing_user.student_id == student_id:
                    return email
                # Otherwise, block it
                raise forms.ValidationError("An account with this email address already exists.")
        return email
    
    def validate_unique(self):
        """
        Instead of deleting the error after it happens, we tell Django 
        to completely skip checking uniqueness for ghost accounts!
        """
        student_id = self.cleaned_data.get('student_id')
        User = get_user_model()
        is_ghost = False
        
        if student_id:
            ghost = User.objects.filter(student_id=student_id, is_active=False).first()
            if ghost:
                self.ghost_user = ghost
                is_ghost = True

        # Get the default list of fields Django plans to exclude from unique checks
        exclude = self._get_validation_exclusions()
        
        if is_ghost:
            # Tell Django: "Do NOT check if student_id or email are unique!"
            exclude.add('student_id')
            exclude.add('email')

        # Now run the actual database validation with our new exclusion rules
        try:
            self.instance.validate_unique(exclude=exclude)
        except forms.ValidationError as e:
            self._update_errors(e)

    def save(self, commit=True):
        """
        If we found a ghost during validation, update it instead of making a new one!
        """
        new_user = super().save(commit=False)
        
        if hasattr(self, 'ghost_user'):
            ghost = self.ghost_user
            
            # Overwrite the ghost's old details with the new form details
            ghost.student_name = new_user.student_name
            ghost.email = new_user.email
            ghost.phone_number = new_user.phone_number
            ghost.password = new_user.password 
            
            if commit:
                ghost.save()
            return ghost
            
        if commit:
            new_user.save()
        return new_user

    def save(self, commit=True):
        """
        If we found a ghost during validation, update it instead of making a new one!
        """
        # This creates a new user object in memory, but hasn't saved to DB yet
        new_user = super().save(commit=False)
        
        # Did we find a ghost account earlier?
        if hasattr(self, 'ghost_user'):
            ghost = self.ghost_user
            
            # Overwrite the ghost's old details with the new form details
            ghost.student_name = new_user.student_name
            ghost.email = new_user.email
            ghost.phone_number = new_user.phone_number
            
            # Copy the securely hashed password over
            ghost.password = new_user.password 
            
            if commit:
                ghost.save()
            return ghost
            
        # If no ghost was found, just save normally!
        if commit:
            new_user.save()
        return new_user


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
    apify_api_key = forms.CharField(
        required=False,
        widget=forms.PasswordInput(render_value=True, attrs={'class': 'input input-bordered w-full', 'placeholder': 'Enter your Apify API key...'}),
        label="Apify API Key"
    )

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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields['apify_api_key'].initial = self.instance.get_apify_api_key()

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

    def save(self, commit=True):
        club = super().save(commit=False)
        raw_key = self.cleaned_data.get('apify_api_key')
        club.set_apify_api_key(raw_key)
        if commit:
            club.save()
        return club



class EventCreationForm(forms.ModelForm):
    existing_post = forms.ModelChoiceField(
        queryset=None, # Set dynamically in __init__
        required=False,
        empty_label="-- Create New Post --",
        widget=forms.Select(attrs={'class': 'select select-bordered w-full focus:border-primary transition-all rounded-xl'}),
        help_text="Optionally, link this event to an existing Instagram post."
    )
    
    description = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'textarea textarea-bordered w-full h-28 focus:border-primary transition-all rounded-xl', 'placeholder': 'e.g. Schedule, RSVP info, requirements, and exciting highlights...'}),
        help_text="Provide a detailed description of the event to display to students."
    )
    
    category = forms.ChoiceField(
        choices=[
            ('WORKSHOP', 'Workshop'),
            ('COMPETITION', 'Competition'),
            ('RECRUITMENT', 'Recruitment'),
            ('INDUSTRIAL_VISIT', 'Industrial Visit'),
            ('ANNOUNCEMENT', 'Announcement'),
        ],
        widget=forms.Select(attrs={'class': 'select select-bordered w-full focus:border-primary transition-all rounded-xl'}),
        initial='WORKSHOP',
        help_text="Select the category that best describes your event."
    )
    
    banner_image = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={'class': 'file-input file-input-bordered w-full rounded-xl'}),
        help_text="Upload a specific banner or image for this event."
    )
    
    class Meta:
        model = Event
        fields = ['title', 'event_date', 'start_time', 'end_time', 'timezone', 'location', 'join_mode', 'fee', 'rsvp_link', 'payment_qr']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'input input-bordered w-full focus:border-primary transition-all rounded-xl', 'placeholder': 'e.g., Annual Tech Symposium'}),
            'event_date': forms.DateInput(attrs={'class': 'input input-bordered w-full focus:border-primary transition-all rounded-xl', 'type': 'date'}),
            'start_time': forms.TimeInput(attrs={'class': 'input input-bordered w-full focus:border-primary transition-all rounded-xl', 'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'class': 'input input-bordered w-full focus:border-primary transition-all rounded-xl', 'type': 'time'}),
            'timezone': forms.TextInput(attrs={'class': 'input input-bordered w-full focus:border-primary transition-all rounded-xl', 'placeholder': 'e.g., GMT+8 (MYT)'}),
            'location': forms.TextInput(attrs={'class': 'input input-bordered w-full focus:border-primary transition-all rounded-xl', 'placeholder': 'e.g., Main Hall'}),
            'join_mode': forms.Select(attrs={'class': 'select select-bordered w-full focus:border-primary transition-all rounded-xl'}),
            'fee': forms.NumberInput(attrs={'class': 'input input-bordered w-full focus:border-primary transition-all rounded-xl', 'step': '0.01'}),
            'rsvp_link': forms.URLInput(attrs={'class': 'input input-bordered w-full focus:border-primary transition-all rounded-xl', 'placeholder': 'https://...'}),
            'payment_qr': forms.FileInput(attrs={'class': 'file-input file-input-bordered w-full focus:border-primary transition-all rounded-xl'}),
        }

    def __init__(self, *args, **kwargs):
        club = kwargs.pop('club', None)
        super().__init__(*args, **kwargs)
        from core.models import Post
        if club:
            # Only show posts that belong to the club and are NOT already linked to an event
            self.fields['existing_post'].queryset = Post.objects.filter(club=club, event__isnull=True).order_by('-timestamp')
            
            # Format the display of the post choices
            self.fields['existing_post'].label_from_instance = lambda obj: f"[{obj.get_category_display()}] {obj.caption[:40]}..." if obj.caption else f"[{obj.get_category_display()}] Post {obj.short_code}"
        else:
            self.fields['existing_post'].queryset = Post.objects.none()

    def clean(self):
        cleaned_data = super().clean()
        join_mode = cleaned_data.get('join_mode')
        fee = cleaned_data.get('fee')
        rsvp_link = cleaned_data.get('rsvp_link')
        existing_post = cleaned_data.get('existing_post')

        if join_mode == 'FEE' and (fee is None or fee <= 0):
            self.add_error('fee', 'You must set a fee greater than 0 for Pay to Join events.')
        if join_mode == 'RSVP' and not rsvp_link:
            self.add_error('rsvp_link', 'You must provide an RSVP link for External RSVP events.')
            
        return cleaned_data


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


class ClubOnboardingForm(forms.ModelForm):
    apify_api_key = forms.CharField(
        required=False,
        widget=forms.PasswordInput(render_value=True, attrs={'class': 'input input-bordered w-full', 'placeholder': 'Enter your Apify API key...'}),
        label="Apify API Key"
    )

    class Meta:
        model = Club
        fields = [
            'logo',
            'banner',
            'renewal_policy',
            'membership_fee',
            'payment_qr_code',
            'social_instagram',
            'social_linkedin',
            'social_twitter',
            'social_facebook',
            'social_discord',
            'social_website',
        ]
        widgets = {
            'logo': forms.FileInput(attrs={'class': 'file-input file-input-bordered w-full max-w-xs'}),
            'banner': forms.FileInput(attrs={'class': 'file-input file-input-bordered w-full max-w-xs'}),
            'renewal_policy': forms.Select(attrs={'class': 'select select-bordered w-full max-w-xs'}),
            'membership_fee': forms.NumberInput(attrs={'class': 'input input-bordered w-full max-w-xs', 'step': '0.01'}),
            'payment_qr_code': forms.FileInput(attrs={'class': 'file-input file-input-bordered w-full max-w-xs'}),
            'social_instagram': forms.URLInput(attrs={'class': 'input input-bordered w-full', 'placeholder': 'https://instagram.com/...'}),
            'social_linkedin': forms.URLInput(attrs={'class': 'input input-bordered w-full', 'placeholder': 'https://linkedin.com/...'}),
            'social_twitter': forms.URLInput(attrs={'class': 'input input-bordered w-full', 'placeholder': 'https://twitter.com/...'}),
            'social_facebook': forms.URLInput(attrs={'class': 'input input-bordered w-full', 'placeholder': 'https://facebook.com/...'}),
            'social_discord': forms.URLInput(attrs={'class': 'input input-bordered w-full', 'placeholder': 'https://discord.gg/...'}),
            'social_website': forms.URLInput(attrs={'class': 'input input-bordered w-full', 'placeholder': 'https://...'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields['apify_api_key'].initial = self.instance.get_apify_api_key()

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

    def save(self, commit=True):
        club = super().save(commit=False)
        raw_key = self.cleaned_data.get('apify_api_key')
        club.set_apify_api_key(raw_key)
        if commit:
            club.save()
        return club

