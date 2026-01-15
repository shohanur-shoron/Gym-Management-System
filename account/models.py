from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.exceptions import ValidationError
from django.utils import timezone
import uuid


class UserManager(BaseUserManager):
    """Custom user manager for email-based authentication"""

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email is required')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('role', 'ADMIN')
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """Custom User model with role-based access"""

    ROLE_CHOICES = [
        ('ADMIN', 'Super Admin'),
        ('MANAGER', 'Gym Manager'),
        ('TRAINER', 'Trainer'),
        ('MEMBER', 'Member'),
    ]

    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]

    email = models.EmailField(unique=True, db_index=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)

    # Optional personal information
    first_name = models.CharField(max_length=255, blank=True, null=True)
    last_name = models.CharField(max_length=255, blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True, null=True)

    gym_branch = models.ForeignKey(
        'gyms.GymBranch',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='users'
    )

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    is_verified = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        db_table = 'users'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['role', 'gym_branch']),
            models.Index(fields=['email']),
        ]

    def __str__(self):
        return f"{self.email} ({self.get_role_display})"

    def clean(self):
        super().clean()
        if self.role == 'ADMIN' and self.gym_branch:
            raise ValidationError({'gym_branch': 'Super Admin cannot belong to a branch.'})

        if self.role != 'ADMIN' and not self.gym_branch:
            raise ValidationError({'gym_branch': 'This role must be assigned to a branch.'})

        # Final safeguard for Trainer limit
        if self.role == 'TRAINER' and self.gym_branch:
            qs = User.objects.filter(gym_branch=self.gym_branch, role='TRAINER')
            if self.pk:
                qs = qs.exclude(pk=self.pk)
            if qs.count() >= 3:
                raise ValidationError('A gym branch cannot have more than 3 trainers.')

        # Super Admin should not have a gym branch
        if self.role == 'ADMIN' and self.gym_branch:
            raise ValidationError({
                'gym_branch': 'Super Admin cannot be assigned to a gym branch'
            })

        # Other roles must have a gym branch
        if self.role != 'ADMIN' and not self.gym_branch:
            raise ValidationError({
                'gym_branch': f'{self.get_role_display} must be assigned to a gym branch'
            })

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    # Helper properties
    @property
    def is_admin(self):
        return self.role == 'ADMIN'

    @property
    def is_manager(self):
        return self.role == 'MANAGER'

    @property
    def is_trainer(self):
        return self.role == 'TRAINER'

    @property
    def is_member(self):
        return self.role == 'MEMBER'

    @property
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def get_role_display(self):
        return self.role

    @property
    def get_gender(self):
        return self.gender

    @property
    def get_gym_branch(self):
        return self.gym_branch


class ActivityLog(models.Model):
    """Track user activities for audit purposes"""

    ACTION_CHOICES = [
        ('CREATE', 'Create'),
        ('UPDATE', 'Update'),
        ('DELETE', 'Delete'),
        ('LOGIN', 'Login'),
        ('LOGOUT', 'Logout'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='activities'
    )
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    model_name = models.CharField(max_length=100)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    details = models.JSONField(null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'activity_logs'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['model_name', 'action']),
        ]

    def __str__(self):
        return f"{self.user} - {self.action} {self.model_name} at {self.created_at}"


class EmailVerificationCode(models.Model):
    PURPOSE_CHOICES = [
        ("signup", "Signup"),
        ("password_reset", "Password Reset"),
        ("2fa", "Two-Factor Auth"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="email_verifications")
    purpose = models.CharField(max_length=50, choices=PURPOSE_CHOICES)

    code_hash = models.CharField(max_length=128)
    token = models.UUIDField(default=uuid.uuid4, editable=False)

    is_used = models.BooleanField(default=False)
    used_at = models.DateTimeField(null=True, blank=True)

    expires_at = models.DateTimeField()
    attempts = models.PositiveIntegerField(default=0)
    max_attempts = models.PositiveIntegerField(default=5)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["user", "purpose", "is_used", "token"]),
            models.Index(fields=["expires_at"]),
        ]
        ordering = ["-created_at"]

    def is_expired(self):
        return timezone.now() > self.expires_at

    def can_attempt(self):
        return not self.is_expired() and not self.is_used and self.attempts < self.max_attempts

    def __str__(self):
        return f"{self.user.email} - {self.purpose} - {'USED' if self.is_used else 'ACTIVE'}"