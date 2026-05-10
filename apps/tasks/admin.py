from django.contrib import admin
from .models import Task, TaskAttachment


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ["title", "workspace", "status", "completion_percentage", "created_by", "updated_at"]
    list_filter = ["status", "workspace"]
    search_fields = ["title"]


@admin.register(TaskAttachment)
class TaskAttachmentAdmin(admin.ModelAdmin):
    list_display = ["filename", "task", "uploaded_by", "uploaded_at"]
