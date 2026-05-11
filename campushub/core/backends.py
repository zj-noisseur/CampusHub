from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models import Q

User = get_user_model()

class DualEmailBackend(ModelBackend):
    """
    Custom authentication backend that allows users to log in using 
    either their primary email or their alternative email.
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None:
            username = kwargs.get(User.USERNAME_FIELD)
        
        try:
            # Check both primary email and alternative email
            user = User.objects.get(Q(email=username) | Q(alternative_email=username))
        except User.DoesNotExist:
            return None
        
        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None
