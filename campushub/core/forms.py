from django import forms
from .models import Club

class ClubSettingsForm(forms.ModelForm):
    class Meta:
        model = Club
        fields = [
            'description',
            'logo',
            'banner',
            'payment_qr',
            'category',
            'social_instagram',
            'social_linkedin',
            'social_facebook',
            'social_twitter',
            'social_website',
            'social_discord',
        ]
        widgets = {
            'description': forms.Textarea(attrs={'class': 'textarea textarea-bordered w-full h-32', 'placeholder': 'Tell us about your club...'}),
            'category': forms.TextInput(attrs={'class': 'input input-bordered w-full', 'placeholder': 'e.g., Technology, Sports, Arts'}),
            'social_instagram': forms.URLInput(attrs={'class': 'input input-bordered w-full', 'placeholder': 'https://instagram.com/yourclub'}),
            'social_linkedin': forms.URLInput(attrs={'class': 'input input-bordered w-full', 'placeholder': 'https://linkedin.com/company/yourclub'}),
            'social_facebook': forms.URLInput(attrs={'class': 'input input-bordered w-full', 'placeholder': 'https://facebook.com/yourclub'}),
            'social_twitter': forms.URLInput(attrs={'class': 'input input-bordered w-full', 'placeholder': 'https://twitter.com/yourclub'}),
            'social_website': forms.URLInput(attrs={'class': 'input input-bordered w-full', 'placeholder': 'https://yourclub.com'}),
            'social_discord': forms.URLInput(attrs={'class': 'input input-bordered w-full', 'placeholder': 'https://discord.gg/yourclub'}),
            'logo': forms.FileInput(attrs={'class': 'file-input file-input-bordered w-full'}),
            'banner': forms.FileInput(attrs={'class': 'file-input file-input-bordered w-full'}),
            'payment_qr': forms.FileInput(attrs={'class': 'file-input file-input-bordered w-full'}),
        }
