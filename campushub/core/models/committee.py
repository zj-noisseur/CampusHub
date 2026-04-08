import uuid
from django.db import models
from django.db import transaction
from django.core.exceptions import ValidationError
from django.db.models import Q
from .user import User
from .club import Club

class Committee(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    club = models.ForeignKey(Club, on_delete=models.CASCADE, related_name='committee')
    designation = models.CharField(max_length=100)
    is_root = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['club'],
                condition=Q(is_root=True),
                name='unique_root_per_club'
            )
        ]

    @property
    def has_admin_access(self):
        return self.is_active and self.club.is_active

    def transaction_root_privileges(self, successor_member):
        if not self.is_root:
            raise ValidationError("Only the admin with root access can initiate a handover")

        with transaction.atomic():
            self.is_root = False
            self.save()
            successor_member.is_root = True
            successor_member.save()