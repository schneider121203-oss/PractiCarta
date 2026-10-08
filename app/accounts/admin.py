from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class PractiCartaUserAdmin(UserAdmin):
    list_display = ("email", "first_name", "last_name", "is_staff", "is_active")
    list_filter = ("is_staff", "is_active", "theme_preference")
    search_fields = ("email", "first_name", "last_name")
    fieldsets = UserAdmin.fieldsets + (("Preferencias", {"fields": ("theme_preference",)}),)
