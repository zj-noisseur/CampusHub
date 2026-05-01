from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.exceptions import ValidationError

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
    email = models.EmailField(unique=True, validators=[validate_mmu_email])
    student_name = models.CharField(max_length=255)
    student_id = models.CharField(max_length=20, blank=True, null=True)
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
        return f"{self.student_name} ({self.email})"

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
    
    def __str__(self):
        return self.name

class ClubManager(models.Model):
    ROLE_CHOICES = [
        ('ROOT', 'Root Admin'),
        ('NON_ROOT', 'Non-Root Admin'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='managed_clubs')
    club = models.ForeignKey(Club, on_delete=models.CASCADE, related_name='managers')
    role = models.CharField(max_length=15, choices=ROLE_CHOICES)
    assigned_date = models.DateTimeField(auto_now_add=True)

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
    submitted_at = models.DateTimeField(auto_now_add=True)

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