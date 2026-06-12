import uuid
from datetime import datetime, timedelta

from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.db.models import Q
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils import timezone


class CustomUserManager(BaseUserManager):
    def create_user(self, email, student_name, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, student_name=student_name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, student_name, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, student_name, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    student_name = models.CharField(max_length=255)
    student_id = models.CharField(max_length=20, blank=True, null=True, unique=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    alternative_email = models.EmailField(max_length=255, blank=True, null=True, unique=True)

    FACULTY_CHOICES = [
        ('FCI', 'Faculty of Computing and Informatics'),
        ('FOM', 'Faculty of Management'),
        ('FAIE', 'Faculty of Artificial Intelligence and Engineering'),
        ('FCM', 'Faculty of Creative Multimedia'),
        ('FAC', 'Faculty of Applied Communication'),
        ('FCA', 'Faculty of Cinematic Arts'),
        ('FOL', 'Faculty of Law'),
        ('FIST', 'Faculty of Information Science and Technology'),
        ('FOB', 'Faculty of Business'),
    ]
    faculty = models.CharField(max_length=50, choices=FACULTY_CHOICES, blank=True, null=True)
    major = models.CharField(max_length=100, blank=True, null=True)

    YEAR_CHOICES = [
        ('Foundation', 'Foundation'),
        ('Diploma', 'Diploma'),
        ('YEAR 1', 'Degree - Year 1'),
        ('YEAR 2', 'Degree - Year 2'),
        ('YEAR 3', 'Degree - Year 3'),
        ('YEAR 4', 'Degree - Year 4'),
        ('Masters', 'Masters'),
        ('PhD', 'PhD'),
    ]
    year_of_study = models.CharField(max_length=20, choices=YEAR_CHOICES, blank=True, null=True)
    joined_clubs = models.ManyToManyField('Club', related_name='members_joined', blank=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    groups = models.ManyToManyField(
        'auth.Group',
        related_name='customuser_auth_groups',
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='customuser_auth_permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['student_name']

    def __str__(self):
        return f"{self.student_name} ({self.email})"

    @property
    def username(self):
        return self.student_name

    @property
    def first_name(self):
        return self.student_name

    @property
    def alt_email(self):
        return self.alternative_email

    @alt_email.setter
    def alt_email(self, value):
        self.alternative_email = value


class UserEmail(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='additional_emails')
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.email


class State(models.Model):
    name = models.CharField(max_length=255, unique=True)
    flag = models.ImageField(upload_to='states/', blank=True, null=True)

    def __str__(self):
        return self.name


class Institution(models.Model):
    university_name = models.CharField(max_length=255, unique=True)
    state = models.ForeignKey(State, on_delete=models.PROTECT)
    logo = models.ImageField(upload_to='institutions/', blank=True, null=True)

    def __str__(self):
        return self.university_name


class Club(models.Model):
    class CategoryChoices(models.IntegerChoices):
        ACADEMIC = 0, 'Academic & Professional'
        SPORTS = 1, 'Sports & Recreation'
        ARTS = 2, 'Arts & Culture'
        COMMUNITY = 3, 'Community Service'
        TECH = 4, 'Technology & Innovation'
        INTEREST = 5, 'Special Interest'
        OTHER = 6, 'Other'

    RENEWAL_CHOICES = [
        ('ROLLING', '1 Year from Join Date'),
        ('CALENDAR', 'Ends December 31st Every Year'),
        ('LIFETIME', 'Pay Once, Never Renew'),
    ]

    institution = models.ForeignKey(Institution, on_delete=models.CASCADE, related_name='clubs')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    club_category = models.PositiveSmallIntegerField(
        choices=CategoryChoices.choices,
        default=CategoryChoices.OTHER,
        null=True,
        blank=True,
    )
    is_claimed = models.BooleanField(default=False)
    membership_fee = models.DecimalField(max_digits=6, decimal_places=2, default=0.00, help_text="Set to 0 if the club is free to join.")
    payment_qr_code = models.ImageField(upload_to='club_qrs/', blank=True, null=True, help_text="Upload your DuitNow or TNG QR code.")
    ig_handle = models.CharField(max_length=255, blank=True, null=True)
    valid_till = models.DateTimeField(null=True, blank=True)
    logo = models.ImageField(upload_to='club_logos/', blank=True, null=True)
    banner = models.ImageField(upload_to='club_banners/', blank=True, null=True)
    payment_qr = models.ImageField(upload_to='club_payment_qrs/', blank=True, null=True)
    social_instagram = models.URLField(max_length=500, blank=True, null=True)
    social_linkedin = models.URLField(max_length=500, blank=True, null=True)
    social_facebook = models.URLField(max_length=500, blank=True, null=True)
    social_twitter = models.URLField(max_length=500, blank=True, null=True)
    social_website = models.URLField(max_length=500, blank=True, null=True)
    social_discord = models.URLField(max_length=500, blank=True, null=True)
    last_fetched_date = models.DateTimeField(null=True, blank=True)
    posts_count = models.PositiveIntegerField(default=0)
    renewal_policy = models.CharField(max_length=20, choices=RENEWAL_CHOICES, default='ROLLING')

    @property
    def is_active(self):
        if not self.valid_till:
            return False
        return self.valid_till > timezone.now()

    @property
    def days_remaining(self):
        """Return the number of whole days remaining until validity expires.
        Returns 0 if the club is expired or has never been activated."""
        if not self.valid_till:
            return 0
        delta = self.valid_till - timezone.now()
        return max(delta.days, 0)

    @property
    def can_extend(self):
        """Extension is allowed only when 30 or fewer days remain."""
        return self.days_remaining <= 30

    @property
    def committee(self):
        if not self.is_active:
            return self.managers.none()
        return self.managers.filter(is_active=True)

    @property
    def category(self):
        if self.club_category is None:
            return None
        class CategoryWrapper:
            def __init__(self, name):
                self.name = name
            def __str__(self):
                return self.name
        return CategoryWrapper(self.get_club_category_display())

    def compute_membership_expiry(self, joined_at=None):
        joined_at = joined_at or timezone.now()
        policy = self.renewal_policy
        if policy == 'ROLLING':
            return joined_at + timedelta(days=365)
        if policy == 'CALENDAR':
            return timezone.make_aware(datetime(joined_at.year, 12, 31, 23, 59, 59))
        return None

    def extend_validity(self, years=1):
        now = timezone.now()
        extension = timedelta(days=365 * years)
        if self.valid_till and self.valid_till > now:
            self.valid_till += extension
        else:
            self.valid_till = now + extension
        self.save(update_fields=['valid_till'])

    def add_committee_member(self, user, designation, role='NON_ROOT'):
        membership = Membership.objects.filter(user=user, club=self).first()
        if not membership:
            membership = Membership.objects.create(
                user=user,
                club=self,
                membership_type='LIMITED',
                status='APPROVED',
                expired_at=self.compute_membership_expiry(),
            )
        elif membership.status != 'APPROVED':
            membership.status = 'APPROVED'
            if membership.expired_at is None:
                membership.expired_at = self.compute_membership_expiry()
            membership.save(update_fields=['status', 'expired_at'])

        return ClubManager.objects.create(
            user=user,
            club=self,
            designation=designation,
            role=role,
            is_active=True,
        )

    def __str__(self):
        return self.name

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['institution', 'name'], name='unique_club_name_per_institution'),
        ]
        indexes = [
            models.Index(fields=['ig_handle']),
            models.Index(fields=['last_fetched_date']),
        ]


class ClubManager(models.Model):
    ROLE_CHOICES = [
        ('ROOT', 'Root Admin'),
        ('NON_ROOT', 'Non-Root Admin'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='managed_clubs')
    club = models.ForeignKey(Club, on_delete=models.CASCADE, related_name='managers')
    role = models.CharField(max_length=15, choices=ROLE_CHOICES)
    designation = models.CharField(max_length=100, blank=True, null=True)
    assigned_date = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        pass

    @property
    def has_admin_access(self):
        return self.is_active and self.club.is_active

    @property
    def has_dashboard_access(self):
        return self.is_active

    @property
    def is_effectively_active(self):
        return self.is_active and self.club.is_active

    @property
    def has_management_powers(self):
        return self.is_effectively_active and self.role == 'ROOT'

    @property
    def role_label(self):
        if not self.is_active:
            return f"Past {self.designation}"
        return self.designation if self.designation else ("Root Admin" if self.role == 'ROOT' else "Member")

    def transfer_root_privileges(self, successor_manager):
        if self.role != 'ROOT':
            raise ValidationError("Only the admin with root access can initiate a handover")
        with transaction.atomic():
            self.role = 'NON_ROOT'
            self.save(update_fields=['role'])
            successor_manager.role = 'ROOT'
            successor_manager.save(update_fields=['role'])

    def toggle_active_status(self, requester):
        if not requester.has_management_powers:
            raise ValidationError("Permission Denied: Only active Root admins can manage members.")
        if self.role == 'ROOT' and self.is_active:
            other_active_roots = ClubManager.objects.filter(
                club=self.club,
                role='ROOT',
                is_active=True
            ).exclude(pk=self.pk).count()
            if other_active_roots == 0:
                raise ValidationError("Critical Error: You cannot deactivate the last active Root manager. Add another Root manager first.")
        self.is_active = not self.is_active
        self.save(update_fields=['is_active'])

    def __str__(self):
        return f"{self.user.student_name} - {self.get_role_display()} of {self.club.name}"


class ClubScrapeStatus(models.Model):
    club = models.OneToOneField('Club', on_delete=models.CASCADE, related_name='scrape_status')
    task_id = models.CharField(max_length=255, blank=True, null=True)
    latest_task_name = models.CharField(max_length=255, blank=True, null=True)
    state = models.CharField(max_length=30, blank=True, null=True)
    phase = models.CharField(max_length=50, blank=True, null=True)
    status = models.CharField(max_length=255, blank=True, null=True)
    current_item = models.PositiveIntegerField(default=0)
    total_items = models.PositiveIntegerField(default=0)
    current_image = models.PositiveIntegerField(default=0)
    total_images = models.PositiveIntegerField(default=0)
    success_count = models.PositiveIntegerField(default=0)
    failure_count = models.PositiveIntegerField(default=0)
    started_at = models.DateTimeField(blank=True, null=True)
    finished_at = models.DateTimeField(blank=True, null=True)
    last_updated_at = models.DateTimeField(auto_now=True)
    extra = models.JSONField(blank=True, null=True)
    failed_items = models.JSONField(default=list, blank=True, null=True, help_text="List of items that failed to process (e.g. image downloads)")

    def mark_completed(self, summary=None):
        self.state = 'SUCCESS'
        self.phase = 'completed'
        self.status = 'Club scrape completed'
        self.finished_at = timezone.now()
        if summary is not None:
            self.extra = summary
        self.save(update_fields=['state', 'phase', 'status', 'finished_at', 'extra'])

    def __str__(self):
        return f"Scrape status for {self.club.name} ({self.state})"


class ClaimRequest(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    club = models.ForeignKey(Club, on_delete=models.CASCADE)
    proof_document = models.FileField(upload_to='claim_proofs/')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    claimer_designation = models.CharField(max_length=100, default='President')
    submitted_at = models.DateTimeField(auto_now_add=True)

    def approve(self):
        with transaction.atomic():
            self.status = 'APPROVED'
            self.save(update_fields=['status'])

    def __str__(self):
        return f"Claim Request: {self.club.name} by {self.user.student_name} ({self.status})"


class Post(models.Model):
    CATEGORY_CHOICES = [
        ('RECRUITMENT', 'Recruitment'),
        ('COMPETITION', 'Competition'),
        ('WORKSHOP', 'Workshop'),
        ('INDUSTRIAL_VISIT', 'Industrial Visit'),
        ('ANNOUNCEMENT', 'Announcement')
    ]

    club = models.ForeignKey(Club, on_delete=models.CASCADE, related_name='posts')
    short_code = models.CharField(max_length=100)
    caption = models.TextField(blank=True)
    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        default='MISC',
    )
    is_event = models.BooleanField(null=True, blank=True)
    timestamp = models.DateTimeField()
    extracted_details = models.JSONField(blank=True, null=True, default=dict, help_text='Parsed event metadata such as date, venue, and registration link.')

    class Meta:
        indexes = [
            models.Index(fields=['club', '-timestamp']),
            models.Index(fields=['-timestamp']),
        ]

    def classify_category(self):
        from core.services.post_categorization import predict_post_category
        self.category = predict_post_category(self.caption)
        self.save(update_fields=['category'])
        return self.category

    def __str__(self):
        return f"{self.club.name} - {self.short_code}"


class PostImage(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='posts/')
    order = models.PositiveIntegerField()

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"Image {self.order} for instagram.com/p/{self.post.short_code}"


class Event(models.Model):
    club = models.ForeignKey(Club, on_delete=models.CASCADE, null=True, blank=True)
    post = models.OneToOneField(Post, on_delete=models.CASCADE, related_name='events')
    title = models.CharField(max_length=255)
    event_date = models.DateField()
    start_time = models.TimeField(blank=True, null=True)
    end_time = models.TimeField(blank=True, null=True)
    timezone = models.CharField(max_length=50, blank=True, null=True, default="GMT+8 (MYT)")
    location = models.CharField(max_length=255)

    @property
    def extracted_details(self):
        return getattr(self.post, 'extracted_details', None)
    
    fee = models.DecimalField(max_digits=6, decimal_places=2, default=0.00, help_text="Set to 0 if the event is free.")
    requires_approval = models.BooleanField(default=False, help_text="If true, host must manually approve attendees.")
    
    JOIN_MODES = [
        ('FREE', 'Free to Join'),
        ('REQUEST', 'Request to Join (Approval required)'),
        ('RSVP', 'External RSVP Link'),
        ('FEE', 'Pay to Join (Requires receipt)'),
    ]
    join_mode = models.CharField(max_length=15, choices=JOIN_MODES, default='FREE')
    rsvp_link = models.URLField(max_length=500, blank=True, null=True, help_text="Link for external RSVP")
    payment_qr = models.ImageField(upload_to='event_payment_qrs/', blank=True, null=True, help_text="Payment QR code for this event")
    
    capacity = models.PositiveIntegerField(blank=True, null=True, help_text="Maximum number of attendees. Leave blank for unlimited.")
    registration_deadline = models.DateTimeField(blank=True, null=True, help_text="When registration closes.")

    STATUS_CHOICES = [
        ('PREPARING', 'Preparing'),
        ('ONGOING', 'Ongoing'),
        ('FINISHED', 'Finished'),
    ]
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='PREPARING')
    qr_token = models.CharField(max_length=64, blank=True, null=True, help_text="Current active token for QR check-in")

    @property
    def is_finished(self):
        return self.status == 'FINISHED'

    class Meta:
        indexes = [models.Index(fields=['event_date'])]

    def __str__(self):
        return self.title


class Attendance(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='attendances')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    guest_name = models.CharField(max_length=255, null=True, blank=True)
    guest_email = models.EmailField(max_length=255, null=True, blank=True)
    guest_phone = models.CharField(max_length=50, null=True, blank=True)
    scanned_at = models.DateTimeField(auto_now_add=True)
    certificate_sent = models.BooleanField(default=False)

    class Meta:
        unique_together = ('event', 'user')

    @property
    def check_in_time(self):
        return self.scanned_at

    def __str__(self):
        if self.user:
            return f"{self.user.student_name} attended {self.event.title}"
        return f"{self.guest_name or 'Guest'} attended {self.event.title}"


class Membership(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('ACTIVE', 'Active'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    ]
    TYPE_CHOICES = [
        ('UNLIMITED', 'Unlimited (Paid)'),
        ('LIMITED', 'Limited (Interest)'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='memberships')
    club = models.ForeignKey(Club, on_delete=models.CASCADE, related_name='members')
    membership_type = models.CharField(max_length=15, choices=TYPE_CHOICES, default='LIMITED')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    payment_proof = models.ImageField(upload_to='payment_proofs/', blank=True, null=True)
    joined_at = models.DateTimeField(auto_now_add=True)
    expired_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.student_name} - {self.club.name} ({self.status})"


class PreRegisteredAttendee(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    event = models.ForeignKey('Event', on_delete=models.CASCADE, related_name='pre_registered')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    guest_email = models.EmailField(max_length=255, blank=True, null=True)
    guest_name = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_ready = models.BooleanField(default=False)
    is_attended = models.BooleanField(default=False)
    
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    ]
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='PENDING')
    receipt = models.ImageField(upload_to='event_receipts/', blank=True, null=True)

    class Meta:
        unique_together = ('event', 'user')

    def __str__(self):
        attendee_name = self.user.student_name if self.user else self.guest_name
        return f"{attendee_name} - {self.event.title}"


class EventCertificate(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='certificates')
    template_image = models.ImageField(upload_to='certificate_templates/')
    name_center_x = models.IntegerField()
    name_center_y = models.IntegerField()
    font_size = models.IntegerField(default=24)
    font_color = models.CharField(max_length=7, default='#000000')
    font_name = models.CharField(
        max_length=50,
        choices=[
            ('Helvetica-Bold', 'Helvetica Bold'),
            ('Helvetica', 'Helvetica Regular'),
            ('Times-Bold', 'Times Bold'),
            ('Times-Roman', 'Times Regular'),
            ('Courier-Bold', 'Courier Bold'),
            ('Courier', 'Courier Regular'),
        ],
        default='Helvetica-Bold'
    )
    custom_text = models.CharField(max_length=255, blank=True, null=True)
    custom_x = models.IntegerField(blank=True, null=True)
    custom_y = models.IntegerField(blank=True, null=True)
    custom_font_size = models.IntegerField(default=20)
    custom_font_color = models.CharField(max_length=7, default='#000000')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Certificate Template for {self.event.title}"


# --- Signals to Sync Attendance ---

@receiver(post_save, sender=Attendance)
def sync_prereg_on_save(sender, instance, created, **kwargs):
    """When an Attendance record is created (via admin or app), mark the PreRegistered record as Present."""
    if created:
        if instance.user:
            PreRegisteredAttendee.objects.filter(event=instance.event, user=instance.user).update(is_attended=True)
        elif instance.guest_email:
            PreRegisteredAttendee.objects.filter(event=instance.event, guest_email=instance.guest_email).update(is_attended=True)


@receiver(post_delete, sender=Attendance)
def sync_prereg_on_delete(sender, instance, **kwargs):
    """When an Attendance record is deleted, mark the PreRegistered record as Absent."""
    if instance.user:
        PreRegisteredAttendee.objects.filter(event=instance.event, user=instance.user).update(is_attended=False)
    elif instance.guest_email:
        PreRegisteredAttendee.objects.filter(event=instance.event, guest_email=instance.guest_email).update(is_attended=False)


@receiver(post_delete, sender=Event)
def delete_mock_post_on_event_delete(sender, instance, **kwargs):
    """When a manually created Event is deleted, also delete its mock Post."""
    post = instance.post
    if post and post.short_code.startswith('manual_'):
        # Delete using the queryset to avoid cascade recursion issues if any
        from core.models import Post
        Post.objects.filter(id=post.id).delete()
