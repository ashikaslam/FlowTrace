from rest_framework import serializers
from .models import QuickNote


class QuickNoteSerializer(serializers.ModelSerializer):
    created_by_username = serializers.CharField(source="created_by.username", read_only=True)
    created_by_role = serializers.CharField(source="created_by.role", read_only=True)

    class Meta:
        model = QuickNote
        fields = [
            "id", "content", "color", "note_type", "is_pinned",
            "created_by_username", "created_by_role", "created_at", "updated_at",
        ]
        read_only_fields = ["color", "created_at", "updated_at"]


class QuickNoteWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuickNote
        fields = ["id", "content", "note_type", "is_pinned"]
        read_only_fields = ["id"]
