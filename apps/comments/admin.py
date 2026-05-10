from django.contrib import admin
from .models import TaskComment, Mention


@admin.register(TaskComment)
class TaskCommentAdmin(admin.ModelAdmin):
    list_display = ["author", "task", "created_at"]
    search_fields = ["body", "author__username"]


@admin.register(Mention)
class MentionAdmin(admin.ModelAdmin):
    list_display = ["mentioned_user", "comment", "is_read", "created_at"]
    list_filter = ["is_read"]
