from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta

# --- Choices Classes ---

class ValidationStatus(models.TextChoices):
    PENDING = 'Pending', 'Pending'
    APPROVED = 'Approved', 'Approved'
    EXPIRED = 'Expired', 'Expired'

class PostCategory(models.TextChoices):
    ANNOUNCEMENT = 'Announcement', 'Announcement'
    RECRUITMENT = 'Recruitment', 'Recruitment'
    WORKSHOP = 'Workshop', 'Workshop'

class PostType(models.TextChoices):
    IMAGE = 'Image', 'Image'
    VIDEO = 'Video', 'Video'
    REEL = 'Reel', 'Reel'

class MembershipStatus(models.TextChoices):
    ACTIVE = 'Active', 'Active'
    EXPIRED = 'Expired', 'Expired'

# --- Models ---

class Institution(models.Model):
    university_name = models.CharField(max_length=255)
    state = models.CharField(max_length=100)

    def __str__(self):
        return self.university_name


class Club(models.Model):
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE, related_name='clubs')
    name = models.CharField(max_length=255)
    ig_handle = models.CharField(max_length=100)
    is_verified = models.BooleanField(default=False)
    
    validation_status = models.CharField(
        max_length=20, 
        choices=ValidationStatus.choices, 
        default=ValidationStatus.PENDING
    )
    valid_till = models.DateTimeField(
        null=True, 
        blank=True, 
        help_text="Approving root user sets this to +365 days"
    )

    def __str__(self):
        return f"{self.name} ({self.institution.university_name})"


class Committee(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    club = models.ForeignKey(Club, on_delete=models.CASCADE, related_name='committee_members')
    academic_year = models.CharField(max_length=9, help_text="e.g. 2025/2026")
    designation = models.CharField(max_length=100)
    is_root = models.BooleanField(
        default=False, 
        help_text="Only the root user can assign other admins"
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = "Committee"

    def __str__(self):
        return f"{self.user.username} - {self.designation} ({self.club.name})"


class Membership(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    club = models.ForeignKey(Club, on_delete=models.CASCADE, related_name='members')
    joined_at = models.DateTimeField(auto_now_add=True)
    academic_year = models.CharField(max_length=9)
    status = models.CharField(
        max_length=20, 
        choices=MembershipStatus.choices, 
        default=MembershipStatus.ACTIVE
    )

    def __str__(self):
        return f"{self.user.username} - {self.club.name} ({self.academic_year})"


class Post(models.Model):
    club = models.ForeignKey(Club, on_delete=models.CASCADE, related_name='posts')
    ig_id = models.CharField(max_length=255, unique=True)
    short_code = models.CharField(max_length=50)
    caption = models.TextField(blank=True, null=True)
    category = models.CharField(
        max_length=50, 
        choices=PostCategory.choices, 
        null=True, 
        blank=True
    )
    type = models.CharField(max_length=20, choices=PostType.choices)
    
    timestamp = models.DateTimeField(help_text="The original Instagram post creation time")
    
    is_edited = models.BooleanField(
        default=False, 
        help_text="Set to true if admin manually overrides scraped data"
    )
    is_public = models.BooleanField(default=True)

    def __str__(self):
        return f"Post {self.short_code} - {self.club.name}"


class LinkClick(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='links')
    url = models.URLField(max_length=500)
    label = models.CharField(max_length=255, help_text="e.g., Registration Form")
    click_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.label} ({self.click_count} clicks)"


class Event(models.Model):
    post = models.OneToOneField(Post, on_delete=models.CASCADE, related_name='event')
    title = models.CharField(max_length=255)
    event_date = models.DateField()
    start_time = models.TimeField()
    location = models.CharField(max_length=255)
    semester = models.PositiveSmallIntegerField(help_text="Standardized school term: 1, 2, or 3")

    def __str__(self):
        return self.title


class PastEventPhoto(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='photos')
    drive_file_id = models.CharField(max_length=255)
    thumbnail_url = models.URLField(max_length=500)
    is_public = models.BooleanField(
        default=False, 
        help_text="If false, only club members can view"
    )

    def __str__(self):
        return f"Photo for {self.event.title}"