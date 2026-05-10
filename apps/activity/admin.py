from django.contrib import admin
from .models import ActivitySession, DeveloperStatus


@admin.register(ActivitySession)
class ActivitySessionAdmin(admin.ModelAdmin):
    list_display = ["membership", "task", "started_at", "ended_at", "completion_at_end"]
    list_filter = ["membership__workspace"]
    search_fields = ["membership__username", "task__title"]


@admin.register(DeveloperStatus)
class DeveloperStatusAdmin(admin.ModelAdmin):
    list_display = ["membership", "current_session", "last_seen"]
