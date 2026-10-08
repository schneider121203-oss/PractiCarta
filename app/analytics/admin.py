from django.contrib import admin

from .models import AnalyticsEvent


@admin.register(AnalyticsEvent)
class AnalyticsEventAdmin(admin.ModelAdmin):
    list_display = ("business", "event_type", "product", "created_at")
    list_filter = ("event_type", "created_at")
    search_fields = ("business__name",)
    readonly_fields = ("business", "product", "event_type", "session_id", "created_at")
