from django.db import models
from django.utils import timezone
from datetime import timedelta
from .user import User
from .club import Club
from .committee import Committee

class ClubClaim(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    club = models.ForeignKey(Club, on_delete=models.CASCADE)
    proof_document = models.FileField(upload_to='claims/proof')
    status = models.CharField(
        max_length=20,
        choices=[('Pending', 'Pending'), ('Approved', 'Approved'), ('Rejected', 'Rejected')],
        default='Pending'
    )
    claimer_designation = models.CharField(max_length=100, default='Member')

    def approve(self):
        self.status = 'Approved'
        self.save()
        self.club.valid_till = timezone.now() + timedelta(days=365)
        self.club.save()
        Committee.objects.create(
            user=self.user,
            club=self.club,
            is_root=True,
            designation=self.claimer_designation
        )