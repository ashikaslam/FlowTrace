from django.contrib import admin
from .models import ActivitySession, DeveloperStatus, CollaborationRequest, TaskCollaborator, CollaborationActivityLog


@admin.register(ActivitySession)
class ActivitySessionAdmin(admin.ModelAdmin):
    list_display = ["membership", "task", "started_at", "ended_at", "completion_at_end"]
    list_filter = ["membership__workspace"]
    search_fields = ["membership__username", "task__title"]


@admin.register(DeveloperStatus)
class DeveloperStatusAdmin(admin.ModelAdmin):
    list_display = ["membership", "current_session", "last_seen"]


@admin.register(CollaborationRequest)
class CollaborationRequestAdmin(admin.ModelAdmin):
    list_display = ["requester", "target", "task", "status", "created_at"]
    list_filter = ["status", "workspace"]
    search_fields = ["requester__username", "target__username", "task__title"]


@admin.register(TaskCollaborator)
class TaskCollaboratorAdmin(admin.ModelAdmin):
    list_display = ["member", "task", "joined_at", "is_active"]
    list_filter = ["is_active"]


@admin.register(CollaborationActivityLog)
class CollaborationActivityLogAdmin(admin.ModelAdmin):
    list_display = ["actor", "task", "action_type", "timestamp"]
    list_filter = ["action_type"]
    search_fields = ["actor__username", "task__title"]
