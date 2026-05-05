import uuid
from datetime import timedelta

from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.db.models import Q
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils import timezone


def validate_mmu_email(value):
    if not value.endswith('@student.mmu.edu.my'):
        raise ValidationError("Only @student.mmu.edu.my email addresses are allowed for Phase 1.")


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
    email = models.EmailField(unique=True, validators=[validate_mmu_email])
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
    CATEGORY_CHOICES = [
        ('RECRUITMENT', 'Recruitment'),
        ('COMPETITION', 'Competition'),
        ('WORKSHOP', 'Workshop'),
        ('PAST_EVENT', 'Past Event'),
        ('MISC', 'Miscellaneous'),
    ]

    institution = models.ForeignKey(Institution, on_delete=models.CASCADE, related_name='clubs')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='MISC')
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

    @property
    def is_active(self):
        if not self.valid_till:
            return False
        return self.valid_till > timezone.now()

    def add_committee_member(self, user, designation):
        if not self.is_active:
            raise ValidationError("Cannot add committee members to an inactive club.")
        return ClubManager.objects.create(
            user=user,
            club=self,
            designation=designation,
            role='NON_ROOT',
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
        constraints = [
            models.UniqueConstraint(
                fields=['club'],
                condition=Q(role='ROOT'),
                name='unique_root_per_club'
            )
        ]

    @property
    def has_admin_access(self):
        return self.is_active and self.club.is_active

    @property
    def has_dashboard_access(self):
        return self.is_active

    @property
    def has_management_powers(self):
        return self.is_active and self.role == 'ROOT'

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
            raise ValidationError("Critical Error: You cannot deactivate the Root admin. Transfer privileges first.")
        self.is_active = not self.is_active
        self.save(update_fields=['is_active'])

    def __str__(self):
        return f"{self.user.student_name} - {self.get_role_display()} of {self.club.name}"


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
    club = models.ForeignKey(Club, on_delete=models.CASCADE, related_name='posts')
    short_code = models.CharField(max_length=100)
    caption = models.TextField(blank=True)
    category = models.CharField(
        max_length=20,
        choices=[
            ('RECRUITMENT', 'Recruitment'),
            ('COMPETITION', 'Competition'),
            ('WORKSHOP', 'Workshop'),
            ('PAST_EVENT', 'Past Event'),
            ('MISC', 'Miscellaneous'),
        ],
        default='MISC',
    )
    timestamp = models.DateTimeField()

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
    location = models.CharField(max_length=255)

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

    def __str__(self):
        if self.user:
            return f"{self.user.student_name} attended {self.event.title}"
        return f"{self.guest_name or 'Guest'} attended {self.event.title}"


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

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='memberships')
    club = models.ForeignKey(Club, on_delete=models.CASCADE, related_name='members')
    membership_type = models.CharField(max_length=15, choices=TYPE_CHOICES, default='LIMITED')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    payment_proof = models.ImageField(upload_to='payment_proofs/', blank=True, null=True)
    joined_at = models.DateTimeField(auto_now_add=True)

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
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Certificate Template for {self.event.title}"
