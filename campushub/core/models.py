from django.db import models, transaction
from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.exceptions import ValidationError
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from datetime import timedelta
import uuid
from django.utils import timezone
from django.db.models import Q

# ==========================================
# 1. USER & AUTHENTICATION
# ==========================================
# Create your models here.
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
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False  )
    email = models.EmailField(unique=True, validators=[validate_mmu_email], 
    help_text = "Please provide your student email address. A confirmation email will be sent for the purpose of account activating your account." )
    student_name = models.CharField(max_length=255)
    student_id = models.CharField(max_length=20, blank=True, null=True, unique=True,
    help_text = "Please provide your student ID.")
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    alt_email = models.EmailField(max_length=255, blank=True, null=True, unique=True)
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
        return f"{self.student_name} ({self.student_id})"
    
    @property
    def username(self):
        return self.student_name
    
    @property
    def first_name(self):
        return self.student_name

# ==========================================
# 2. CORE SYSTEM
# ==========================================

class Club(models.Model):
        
    CATEGORY_CHOICES = [
        ('RECRUITMENT', 'Recruitment'),
        ('COMPETITION', 'Competition'),
        ('WORKSHOP', 'Workshop'),
        ('PAST_EVENT', 'Past Event'),
        ('MISC', 'Miscellaneous'),
    ]

    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='MISC')
    is_claimed = models.BooleanField(default=False)

    class Institution(models.Model):
        university_name = models.CharField(max_length=255, unique=True)
        state = models.CharField(max_length=255)
        def __str__(self):
            return self.university_name
        
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE, related_name='clubs', null=True, blank=True)
    ig_handle = models.CharField(max_length=255, blank=True, null=True) 
    valid_till = models.DateTimeField(null=True, blank=True)

    # Branding & Info
    logo = models.ImageField(upload_to='club_logos/', blank=True, null=True)
    banner = models.ImageField(upload_to='club_banners/', blank=True, null=True)
    payment_qr = models.ImageField(upload_to='club_payment_qrs/', blank=True, null=True)
    
    # Social Links
    social_instagram = models.URLField(max_length=500, blank=True, null=True)
    social_linkedin = models.URLField(max_length=500, blank=True, null=True)
    social_facebook = models.URLField(max_length=500, blank=True, null=True)
    social_twitter = models.URLField(max_length=500, blank=True, null=True)
    social_website = models.URLField(max_length=500, blank=True, null=True)
    social_discord = models.URLField(max_length=500, blank=True, null=True)

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
            is_active=True
        )


    
    def __str__(self):
        return self.name

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
            self.save()

            successor_manager.role = 'ROOT'
            successor_manager.save()

    def toggle_active_status(self, requester):
        if not requester.has_management_powers:
            raise ValidationError("Permission Denied: Only active Root admins can manage members.")
        
        if self.role == 'ROOT' and self.is_active:
            raise ValidationError("Critical Error: You cannot deactivate the Root admin. Transfer privileges first.")

        self.is_active = not self.is_active
        self.save()


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
            self.save()

            self.club.is_claimed = True
            self.club.valid_till = timezone.now() + timedelta(days=365)
            self.club.save()

            ClubManager.objects.create(
                user=self.user,
                club=self.club,
                role='ROOT',
                designation=self.claimer_designation
            )

    def __str__(self):
        return f"Claim Request: {self.club.name} by {self.user.student_name} ({self.status})"

class Membership(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('ACTIVE', 'Active'),
        ('REJECTED', 'Rejected'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='memberships')
    club = models.ForeignKey(Club, on_delete=models.CASCADE, related_name='members')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    payment_proof = models.ImageField(upload_to='payment_proofs/', blank=True, null=True)
    joined_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.student_name} - {self.club.name} ({self.status})"
    


# ==========================================
# 3. CONTENT & EVENTS
# ==========================================

class Post(models.Model):
    club = models.ForeignKey(Club, on_delete=models.CASCADE, related_name='posts')
    ig_id = models.CharField(max_length=255, unique=True)
    short_code = models.CharField(max_length=100)
    caption = models.TextField(blank=True)
    
    image_url = models.URLField(max_length=500, blank=True) 
    local_image = models.ImageField(upload_to='posts/ig/', null=True, blank=True) 
    
    timestamp = models.DateTimeField()

class Event(models.Model):
    club = models.ForeignKey(Club, on_delete=models.CASCADE, related_name='events', null=True, blank=True)
    post = models.OneToOneField(Post, on_delete=models.CASCADE, related_name='events', null=True, blank=True)
    
    title = models.CharField(max_length=255)
    event_date = models.DateField()
    location = models.CharField(max_length=255)
    
    STATUS_CHOICES = [
        ('PREPARING', 'Preparing'),
        ('ONGOING', 'Ongoing'),
        ('FINISHED', 'Finished'),
    ]
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='PREPARING')

    @property
    def is_finished(self):
        return self.status == 'FINISHED'

    def __str__(self):
        return self.title

class PreRegisteredAttendee(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='pre_registered')
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    email = models.EmailField(max_length=255, null=True, blank=True) 
    name = models.CharField(max_length=255, null=True, blank=True) 
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    is_ready = models.BooleanField(default=False)
    is_attended = models.BooleanField(default=False)

    class Meta:
        unique_together = ('event', 'user')

    def __str__(self):
        attendee_name = self.user.student_name if self.user else self.name
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

class Attendance(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='attendances')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    
    guest_name = models.CharField(max_length=255, null=True, blank=True)
    guest_email = models.EmailField(max_length=255, null=True, blank=True)
    guest_phone = models.CharField(max_length=50, null=True, blank=True)
    
    check_in_time = models.DateTimeField(auto_now_add=True)
    certificate_sent = models.BooleanField(default=False)

    class Meta:
        unique_together = ('event', 'user') 

    def __str__(self):
        attendee_name = self.user.student_name if self.user else self.guest_name
        return f"{attendee_name} - {self.event.title}"

# --- Signals to Sync Attendance ---

@receiver(post_save, sender=Attendance)
def sync_prereg_on_save(sender, instance, created, **kwargs):
    """When an Attendance record is created (via admin or app), mark the PreRegistered record as Present."""
    if created:
        if instance.user:
            PreRegisteredAttendee.objects.filter(event=instance.event, user=instance.user).update(is_attended=True)
        elif instance.guest_email:
            PreRegisteredAttendee.objects.filter(event=instance.event, email=instance.guest_email).update(is_attended=True)

@receiver(post_delete, sender=Attendance)
def sync_prereg_on_delete(sender, instance, **kwargs):
    """When an Attendance record is deleted, mark the PreRegistered record as Absent."""
    if instance.user:
        PreRegisteredAttendee.objects.filter(event=instance.event, user=instance.user).update(is_attended=False)
    elif instance.guest_email:
        PreRegisteredAttendee.objects.filter(event=instance.event, email=instance.guest_email).update(is_attended=False)
