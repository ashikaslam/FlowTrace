from rest_framework import serializers
from .models import TaskComment, Mention


class MentionSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="mentioned_user.username", read_only=True)

    class Meta:
        model = Mention
        fields = ["id", "username", "is_read", "created_at"]


class TaskCommentSerializer(serializers.ModelSerializer):
    author_username = serializers.CharField(source="author.username", read_only=True)
    mentions = MentionSerializer(many=True, read_only=True)

    class Meta:
        model = TaskComment
        fields = ["id", "body", "author_username", "mentions", "created_at", "updated_at"]
        read_only_fields = ["created_at", "updated_at"]
