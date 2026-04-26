from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

User = get_user_model()

class DualEmailBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            # First, try to log them in with their official MMU email
            user = User.objects.get(email=username)
        except User.DoesNotExist:
            try:
                # If that fails, try checking the alternative personal email!
                user = User.objects.get(alt_email=username)
            except User.DoesNotExist:
                return None # No account found with either email

        # If we found the user, verify their password
        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None