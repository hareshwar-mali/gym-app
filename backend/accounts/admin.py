from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import GymUser, Gym, GymProfile


@admin.register(GymUser)
class GymUserAdmin(UserAdmin):
    list_display = ['id', 'email', 'role', 'is_active', 'created_at']
    list_filter = ['role', 'is_active']
    search_fields = ['email']
    ordering = ['-created_at']
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Info', {'fields': ('role',)}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
    )
    add_fieldsets = (
        (None, {'fields': ('email', 'password1', 'password2', 'role')}),
    )


@admin.register(Gym)
class GymAdmin(admin.ModelAdmin):
    list_display = ['id', 'gym_name', 'owner_name', 'mobile', 'city', 'status', 'created_at']
    list_filter = ['status', 'state']
    search_fields = ['gym_name', 'owner_name', 'mobile', 'email', 'city']


@admin.register(GymProfile)
class GymProfileAdmin(admin.ModelAdmin):
    list_display = ['id', 'gym']