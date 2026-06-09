from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin


class GymUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email is required')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'super_admin')
        return self.create_user(email, password, **extra_fields)


class GymUser(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = [
        ('super_admin', 'Super Admin'),
        ('gym_owner', 'Gym Owner'),
    ]

    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='gym_owner')
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    objects = GymUserManager()

    def __str__(self):
        return self.email


class Gym(models.Model):
    STATUS_CHOICES = [
        ('trial_active', 'Trial Active'),
        ('trial_expired', 'Trial Expired'),
        ('active', 'Active'),
        ('expiring_soon', 'Expiring Soon'),
        ('expired', 'Expired'),
        ('blocked', 'Blocked'),
        ('cancelled', 'Cancelled'),
    ]

    user = models.OneToOneField(GymUser, on_delete=models.CASCADE, related_name='gym')
    gym_name = models.CharField(max_length=200)
    owner_name = models.CharField(max_length=200)
    mobile = models.CharField(max_length=15, unique=True)
    email = models.EmailField()
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    opening_time = models.TimeField(null=True, blank=True)
    closing_time = models.TimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='trial_active')
    trial_start_date = models.DateField(null=True, blank=True)
    trial_end_date = models.DateField(null=True, blank=True)
    subscription_end_date = models.DateField(null=True, blank=True)
    is_blocked = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.gym_name} — {self.owner_name}"

    class Meta:
        ordering = ['-created_at']


class GymProfile(models.Model):
    gym = models.OneToOneField(Gym, on_delete=models.CASCADE, related_name='profile')
    logo = models.ImageField(upload_to='gym_logos/', null=True, blank=True)
    about_gym = models.TextField(blank=True)
    trainer_details = models.TextField(blank=True)
    membership_pricing = models.TextField(blank=True)
    facilities = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Profile — {self.gym.gym_name}"
