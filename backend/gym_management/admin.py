from django.contrib import admin
from .models import Member, Attendance, Payment, ClassSchedule


@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'mobile', 'gym', 'membership_plan', 'membership_end_date', 'membership_status']
    list_filter = ['membership_status', 'gender']
    search_fields = ['name', 'mobile', 'gym__gym_name']


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ['id', 'member', 'gym', 'attendance_date', 'status', 'check_in_time']
    list_filter = ['status', 'attendance_date']
    search_fields = ['member__name', 'gym__gym_name']


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['id', 'member', 'gym', 'amount', 'paid_amount', 'due_amount', 'payment_status', 'payment_date']
    list_filter = ['payment_status', 'payment_mode']
    search_fields = ['member__name', 'gym__gym_name']


@admin.register(ClassSchedule)
class ClassScheduleAdmin(admin.ModelAdmin):
    list_display = ['id', 'class_name', 'gym', 'trainer_name', 'day', 'start_time', 'is_active']
    list_filter = ['day', 'is_active']
    search_fields = ['class_name', 'gym__gym_name']
