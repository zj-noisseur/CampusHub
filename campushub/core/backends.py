from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models import Q
from .models import UserEmail

# This grabs your custom User model
User = get_user_model()

class DualEmailBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            # 1. First, check if they are logging in with their Primary Email
            user = User.objects.get(email=username)
        except User.DoesNotExist:
            # 2. If not, check if it matches any of their Additional Emails
            try:
                user_email = UserEmail.objects.get(email=username)
                user = user_email.user # Grab the user attached to this email
            except UserEmail.DoesNotExist:
                return None # No email found at all

        # 3. Check the password
        if user.check_password(password) and self.user_can_authenticate(user):
            return user
            
        return None