from rest_framework import serializers
from .models import ActivitySession, DeveloperStatus


class ActivitySessionSerializer(serializers.ModelSerializer):
    task_title = serializers.CharField(source="task.title", read_only=True)
    task_id = serializers.IntegerField(source="task.id", read_only=True)
    username = serializers.CharField(source="membership.username", read_only=True)
    duration_seconds = serializers.IntegerField(read_only=True)

    class Meta:
        model = ActivitySession
        fields = [
            "id", "task_id", "task_title", "username",
            "started_at", "ended_at", "duration_seconds",
            "completion_at_start", "completion_at_end", "switch_note",
        ]


class StartSessionSerializer(serializers.Serializer):
    task_id = serializers.IntegerField()
    completion_percentage = serializers.IntegerField(min_value=0, max_value=100, required=False, default=0)


class SwitchTaskSerializer(serializers.Serializer):
    next_task_id = serializers.IntegerField()
    completion_percentage = serializers.IntegerField(min_value=0, max_value=100)
    note = serializers.CharField(required=False, allow_blank=True, default="")


class DeveloperStatusSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="membership.username", read_only=True)
    current_task = serializers.SerializerMethodField()
    last_seen = serializers.DateTimeField(read_only=True)

    class Meta:
        model = DeveloperStatus
        fields = ["username", "current_task", "last_seen"]

    def get_current_task(self, obj):
        if obj.current_session:
            return {
                "id": obj.current_session.task.id,
                "title": obj.current_session.task.title,
                "started_at": obj.current_session.started_at,
                "completion": obj.current_session.task.completion_percentage,
            }
        return None
