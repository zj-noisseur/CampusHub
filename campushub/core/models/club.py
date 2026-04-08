from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from .institution import Institution

class Club(models.Model):
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE, related_name='clubs')
    name = models.CharField(max_length=255)
    ig_handle = models.CharField(max_length=255, null=True, blank=True)
    valid_till = models.DateTimeField(null=True, blank=True)

    @property
    def is_active(self):
        if not self.valid_till:
            return False
        return self.valid_till > timezone.now()

    def add_committee_member(self, user, designation):
        from .committee import Committee
        if not self.is_active:
            raise ValidationError("Cannot add committee members to an inactive club.")

        return Committee.objects.create(
            user=user,
            club=self,
            designation=designation,
            is_root=False,
            is_active=True
        )

    def __str__(self):
        return self.name