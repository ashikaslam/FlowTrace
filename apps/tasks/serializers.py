from rest_framework import serializers
from .models import Task, TaskAttachment


class TaskAttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskAttachment
        fields = ["id", "file", "filename", "uploaded_at"]


class TaskSerializer(serializers.ModelSerializer):
    attachments = TaskAttachmentSerializer(many=True, read_only=True)
    created_by_username = serializers.CharField(source="created_by.username", read_only=True)

    class Meta:
        model = Task
        fields = [
            "id", "title", "description", "status", "completion_percentage",
            "created_by_username", "attachments", "created_at", "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]


class TaskCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ["id", "title", "description"]


class TaskUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ["title", "description", "completion_percentage"]
