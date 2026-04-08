from django.db import models
import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models, transaction
from django.utils import timezone
from datetime import timedelta
from django.core.exceptions import ValidationError
from django.db.models import Q

"""
1.
"""
class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    email = models.EmailField(unique=True, help_text="Please provide your student email address. A confirmation email will be sent for the purpose of activating your account.")

    student_id = models.CharField(
        max_length=10,
        unique=True,
        help_text="Please provide your student ID."
    )
    
    def __str__(self):
        return f"{self.username} ({self.student_id})"
    
"""
2.
"""
class Institution(models.Model):
    university_name = models.CharField(max_length=255, unique=True)

    state = models.CharField(max_length=255)

    def __str__(self):
        return self.university_name

"""
3.
"""
class Club(models.Model):
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE, related_name='clubs')

    name = models.CharField(max_length=255)

    ig_hanlde = models.CharField(max_length=255)

    valid_till = models.DateTimeField(null=True, blank=True)

    # to all clubs are valid, the associated admins have to make sure to check their email annually to maintain the verified checkmark
    @property
    def is_active(self):
        if not self.valid_till:
            return False
        return self.valid_till > timezone.now()
    
    def add_committee_member(self, user, designation):
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


"""
4.
"""
class Committee(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    club = models.ForeignKey(Club, on_delete=models.CASCADE, related_name='committee')

    # ideally this should be optional and not strictly necessary but merely informational for displaying the organisational chart only
    designation = models.CharField(max_length=100)

    # the first person initiating the claiming process will be assigned true for is_root 
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

    def trasaction_root_privileges(self, successor_member):
        if not self.is_root:
            raise ValidationError("Only the admin with root access can initiate a handover")

        with transaction.atomic():
            self.is_root = False
            self.save()

            successor_member.is_root = True
            successor_member.save()
    

    

"""
5.
"""
class ClubClaim(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    club = models.ForeignKey(Club, on_delete=models.CASCADE)

    proof_document = models.FileField(upload_to='claims/proof')

    status = models.CharField(
        max_length=20,
        choices=[(
            'Pending', 'Pending'
        ), (
            'Approved', 'Approved'
        ), (
            'Rejected', 'Rejected'
        )],
        default='Pending'
    )

    def approve(self):
        self.status = 'Approved'
        self.save()

        self.club.valid_till = timezone.now() + timedelta(days=365)
        self.club.save()

        Committee.objects.create(
            user=self.user,
            club=self.club,
            is_root=True,
            # TO NOTE: this is only for the first person performing the action
            designation=self.claimer_designation
        )
"""
6.
"""
class Post(models.Model):
    club = models.ForeignKey(Club, on_delete=models.CASCADE, related_name='posts')

    ig_id = models.CharField(max_length=255, unique=True)

    # unique identifier for a particular post, at the end of the post route in Instagram
    short_code = models.CharField(max_length=100)

    caption = models.TextField(blank=True)

    # TO NOTE: this is ambiguous. Timestamp should ideally and strictly be the timestamp when the post was originally posted on Instagram 
    timestamp = models.DateTimeField()

"""
7. this is the model that keeps track of all the events that is associated with a post
"""
class Event(models.Model):
    # one-to-one relation to prevent duplicates, so that all events can be associated to just one post only, some clubs might post in duplicates for promotional purposes 
    post = models.OneToOneField(Post, on_delete=models.CASCADE, related_name='events')
    
    # these fields are to be inferred from the caption itself
    title = models.CharField(max_length=255)
    event_date = models.DateField()
    location = models.CharField(max_length=255)


"""
8. 
"""
class Attendance(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='attendance_records')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    # TO NOTE whether to drop or implement this at all as this is assuming the event is public and accepts walk-ins
    guest_name = models.CharField(max_length=255, blank=True)
    
    scanned_at = models.DateTimeField(auto_now_add=True)

"""
9.
"""
class CertificateTemplate(models.Model):
    club = models.ForeignKey(Club, on_delete=models.CASCADE)

    # TO NOTE: the endpoint to be uploaded to has to be reviewed and pending changes, am considering to assign this to the dashboard enpoint instead
    template_image = models.ImageField(upload_to='certificates/templates')

    # TO NOTE: not really sure what these are meant for yet
    name_x_pos = models.IntegerField(default=500)
    name_y_pos = models.IntegerField(default=500)