from django.contrib import admin
from .models import SubscriptionPlan, Subscription, ManualSubscriptionPayment


@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'duration_days', 'price', 'is_active']


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ['id', 'gym', 'plan', 'start_date', 'end_date', 'status']
    list_filter = ['status']
    search_fields = ['gym__gym_name', 'gym__mobile']


@admin.register(ManualSubscriptionPayment)
class ManualSubscriptionPaymentAdmin(admin.ModelAdmin):
    list_display = ['id', 'gym', 'plan', 'amount', 'payment_mode', 'payment_date', 'status']
    list_filter = ['status', 'payment_mode']
    search_fields = ['gym__gym_name', 'gym__mobile']