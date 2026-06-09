from django.db import models
from accounts.models import Gym


class Member(models.Model):
    GENDER_CHOICES = [('male', 'Male'), ('female', 'Female'), ('other', 'Other')]
    STATUS_CHOICES = [('active', 'Active'), ('inactive', 'Inactive'), ('expired', 'Expired')]

    gym = models.ForeignKey(Gym, on_delete=models.CASCADE, related_name='members')
    name = models.CharField(max_length=200)
    mobile = models.CharField(max_length=15)
    email = models.EmailField(blank=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True)
    age = models.PositiveIntegerField(null=True, blank=True)
    address = models.TextField(blank=True)
    joining_date = models.DateField()
    membership_plan = models.CharField(max_length=200, blank=True)
    membership_start_date = models.DateField()
    membership_end_date = models.DateField()
    membership_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    payment_status = models.CharField(max_length=20, default='paid')
    fitness_goal = models.CharField(max_length=200, blank=True)
    assigned_trainer = models.CharField(max_length=200, blank=True)
    photo = models.ImageField(upload_to='member_photos/', null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} — {self.gym.gym_name}"

    class Meta:
        ordering = ['-created_at']


class Attendance(models.Model):
    STATUS_CHOICES = [('present', 'Present'), ('absent', 'Absent')]

    gym = models.ForeignKey(Gym, on_delete=models.CASCADE, related_name='attendance')
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='attendance')
    attendance_date = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='present')
    check_in_time = models.TimeField(null=True, blank=True)
    remarks = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.member.name} — {self.attendance_date} — {self.status}"

    class Meta:
        ordering = ['-attendance_date']
        unique_together = ['gym', 'member', 'attendance_date']


class Payment(models.Model):
    STATUS_CHOICES = [('paid', 'Paid'), ('pending', 'Pending'), ('partial', 'Partial')]
    MODE_CHOICES = [
        ('cash', 'Cash'),
        ('upi', 'UPI'),
        ('card', 'Card'),
        ('bank_transfer', 'Bank Transfer'),
        ('other', 'Other'),
    ]

    gym = models.ForeignKey(Gym, on_delete=models.CASCADE, related_name='payments')
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    due_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    payment_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='paid')
    payment_mode = models.CharField(max_length=20, choices=MODE_CHOICES, default='cash')
    payment_date = models.DateField()
    remarks = models.CharField(max_length=300, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.member.name} — ₹{self.amount} — {self.payment_status}"

    class Meta:
        ordering = ['-payment_date']


class ClassSchedule(models.Model):
    DAY_CHOICES = [
        ('monday', 'Monday'), ('tuesday', 'Tuesday'), ('wednesday', 'Wednesday'),
        ('thursday', 'Thursday'), ('friday', 'Friday'), ('saturday', 'Saturday'),
        ('sunday', 'Sunday'),
    ]

    gym = models.ForeignKey(Gym, on_delete=models.CASCADE, related_name='classes')
    class_name = models.CharField(max_length=200)
    icon = models.CharField(max_length=10, default='🏋️')
    trainer_name = models.CharField(max_length=200)
    day = models.CharField(max_length=20, choices=DAY_CHOICES)
    start_time = models.TimeField()
    end_time = models.TimeField()
    capacity = models.PositiveIntegerField(default=20)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.class_name} — {self.gym.gym_name} — {self.day}"

    class Meta:
        ordering = ['day', 'start_time']
