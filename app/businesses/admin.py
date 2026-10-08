from django.contrib import admin

from .models import Business


@admin.register(Business)
class BusinessAdmin(admin.ModelAdmin):
    list_display = ("name", "owner", "subscription_status", "subscription_expires_at", "is_published", "created_at")
    list_filter = ("subscription_status", "is_published", "brand_palette")
    search_fields = ("name", "owner__email", "whatsapp_number")
    readonly_fields = ("created_at", "updated_at")
