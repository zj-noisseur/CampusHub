from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models import Q

# This grabs your custom User model
User = get_user_model()

class DualEmailBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None:
            username = kwargs.get(User.USERNAME_FIELD)
            
        try:
            # The Magic Line: Search for a user where email matches OR alt_email matches
            user = User.objects.get(Q(email=username) | Q(alt_email=username))
            
        except User.DoesNotExist:
            # No matching primary or alt email found
            return None
            
        except User.MultipleObjectsReturned:
            # Security fail-safe in case two accounts somehow have the same alt email
            return User.objects.filter(Q(email=username) | Q(alt_email=username)).order_by('id').first()

        # We found a user! Now check if the password they typed is correct
        if user.check_password(password) and self.user_can_authenticate(user):
            return user
            
        return None