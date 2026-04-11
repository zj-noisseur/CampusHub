from django.db import models
import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models, transaction
from django.utils import timezone
from datetime import timedelta
from django.core.exceptions import ValidationError
from django.db.models import Q

from core import settings

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
2.A
"""
class State(models.Model):
    name = models.CharField(max_length=255, unique=True)
    flag = models.ImageField(
        upload_to='states/',
        blank=True,
        null=True     
    )

    def __str__(self):
        return self.name

"""
2.B
"""
class Institution(models.Model):
    university_name = models.CharField(max_length=255, unique=True)

    state = models.ForeignKey(State, on_delete=models.PROTECT)

    logo = models.ImageField(
        upload_to='institutions/',
        blank=True,
        null=True
    )

    

    def __str__(self):
        return self.university_name

"""
3.
"""
class Club(models.Model):
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE, related_name='clubs')

    name = models.CharField(max_length=255)

    ig_handle = models.CharField(max_length=255, null=True, blank=True)

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
3.
"""
class Committee(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    club = models.ForeignKey(Club, on_delete=models.CASCADE, related_name='committee')

    # ideally this should be optional and not strictly necessary but merely informational for displaying the organisational chart only
    designation = models.CharField(max_length=100)

    # no longer set to only one person able to be the root user
    # all is_active members are able to access the dashboard
    # is_root allows to add is_active members (ie committee) and toggle is_root status (if at least one remaining) and also is_active status to off 
    is_root = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)


    @property
    def has_dashboard_access(self):
        """Allows login to the portal as long as they are an active member."""
        return self.is_active

    @property
    def has_management_powers(self):
        """Allows managing other members. Must be both a Root and Active."""
        return self.is_active and self.is_root

    @property
    def role_label(self):
        """Convenience property for the Org Chart UI."""
        if not self.is_active:
            return f"Past {self.designation}"
        return self.designation if self.designation else ("Root Admin" if self.is_root else "Member")

    # --- Business Logic Methods ---

    def _verify_leadership_safety(self):
        """
        Internal safety check: Ensures a club always has at least one 
        active Root admin before a change is committed.
        """
        active_roots = self.club.committee.filter(
            is_root=True, 
            is_active=True
        ).count()
        if active_roots <= 1:
            raise ValidationError(
                "Critical Error: You cannot demote or deactivate the last remaining Root admin. "
                "Promote another member first."
            )

    def toggle_active_status(self, requester):
        """
        Allows a Root admin to 'deactivate' a member (e.g., Graduation).
        This keeps the record for the Org Chart but revokes dashboard access.
        """
        if not requester.has_management_powers:
            raise ValidationError("Permission Denied: Only active Root admins can manage members.")
        
        # Guardrail: Prevents the last active Root user from setting himself or herself to inactive, without a remaning root user in place, no non-root user can promote themselves to possess root access
        if self.is_root and self.is_active:
            self._verify_leadership_safety()

        self.is_active = not self.is_active
        self.save()

    def toggle_root_status(self, requester):
        """Promote or demote members between Root and Standard levels."""
        if not requester.has_management_powers:
            raise ValidationError("Permission Denied: Only active Root admins can change roles.")

        # Guardrail: Prevent demoting the last active Root
        if self.is_root and self.is_active:
            self._verify_leadership_safety()

        self.is_root = not self.is_root
        self.save()
    

    

"""
4.
"""
class ClubClaim(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    club = models.ForeignKey(Club, on_delete=models.CASCADE)

    claimer_designation = models.CharField(
        max_length=100,
        default='Club Admin'
    )

    proof_document = models.FileField(upload_to='clubclaims/')

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
        # the idea is to make sure the committee keep their club profile active 
        self.club.valid_till = timezone.now() + timedelta(days=365)
        self.club.save()

        Committee.objects.create(
            user=self.user,
            club=self.club,
            is_root=True,
            designation=self.claimer_designation
        )
"""
5.
"""
class Post(models.Model):
    club = models.ForeignKey(Club, on_delete=models.CASCADE, related_name='posts')

    ig_id = models.CharField(max_length=255, unique=True)

    # unique identifier for a particular post, at the end of the post route in Instagram
    short_code = models.CharField(max_length=100)

    caption = models.TextField(blank=True)
    image_url = models.URLField(max_length=500, blank=True) # Remote IG link
    local_image = models.ImageField(upload_to='posts/', null=True, blank=True) # Your local copy

    # TO NOTE: this is ambiguous. Timestamp should ideally and strictly be the timestamp when the post was originally posted on Instagram 
    timestamp = models.DateTimeField()

"""
6. this is the model that keeps track of all the events that is associated with a post
"""
class Event(models.Model):
    # one-to-one relation to prevent duplicates, so that all events can be associated to just one post only, some clubs might post in duplicates for promotional purposes 
    post = models.OneToOneField(Post, on_delete=models.CASCADE, related_name='events')
    
    # these fields are to be inferred from the caption itself
    title = models.CharField(max_length=255)
    event_date = models.DateField()
    location = models.CharField(max_length=255)


"""
7. 
"""
class Attendance(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    event = models.ForeignKey('Event', on_delete=models.CASCADE, related_name='attendances')
    
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Guest details for non-registered users
    guest_name = models.CharField(max_length=255, null=True, blank=True)
    guest_email = models.EmailField(max_length=255, null=True, blank=True)
    guest_phone = models.CharField(max_length=50, null=True, blank=True)
    
    # Attendance metadata
    scanned_at = models.DateTimeField(auto_now_add=True)
    certificate_sent = models.BooleanField(default=False)

    def __str__(self):
        attendee_name = self.user.username if self.user else self.guest_name
        return f"{attendee_name} - {self.event.title}"


"""
8. 
"""
class Membership(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('ACTIVE', 'Active'),
        ('REJECTED', 'Rejected'),
    ]
    
    TYPE_CHOICES = [
        ('UNLIMITED', 'Unlimited (Paid)'),
        ('LIMITED', 'Limited (Interest)'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='memberships')
    club = models.ForeignKey(Club, on_delete=models.CASCADE, related_name='members')
    membership_type = models.CharField(max_length=15, choices=TYPE_CHOICES)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    payment_proof = models.ImageField(upload_to='memberships/', blank=True, null=True)
    joined_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.student_id} - {self.club.name} ({self.status})"

"""
9. 
"""    
class PreRegisteredAttendee(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    event = models.ForeignKey('Event', on_delete=models.CASCADE, related_name='pre_registered')
    
    email = models.EmailField(max_length=255)
    name = models.CharField(max_length=255, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('event', 'email')

    def __str__(self):
        return f"{self.name or self.email} - {self.event.title}"

"""
10.
"""
class EventCertificate(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    event = models.ForeignKey('Event', on_delete=models.CASCADE, related_name='certificates')
    
    template_image = models.ImageField(upload_to='certificate_templates/')
    
    name_center_x = models.IntegerField()
    name_center_y = models.IntegerField()
    font_size = models.IntegerField(default=24)
    font_color = models.CharField(max_length=7, default='#000000') 
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Certificate Template for {self.event.title}"
