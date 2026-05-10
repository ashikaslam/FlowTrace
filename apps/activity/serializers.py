from rest_framework import serializers
from .models import ActivitySession, DeveloperStatus, CollaborationRequest, TaskCollaborator, CollaborationActivityLog


class ActivitySessionSerializer(serializers.ModelSerializer):
    task_title = serializers.CharField(source="task.title", read_only=True)
    task_id = serializers.IntegerField(source="task.id", read_only=True)
    username = serializers.CharField(source="membership.username", read_only=True)
    duration_seconds = serializers.IntegerField(read_only=True)
    collaborators = serializers.SerializerMethodField()

    class Meta:
        model = ActivitySession
        fields = [
            "id", "task_id", "task_title", "username",
            "started_at", "ended_at", "duration_seconds",
            "completion_at_start", "completion_at_end", "switch_note",
            "collaborators",
        ]

    def get_collaborators(self, obj):
        collabs = TaskCollaborator.objects.filter(
            task=obj.task, is_active=True
        ).exclude(member=obj.membership).select_related("member")
        return [c.member.username for c in collabs]


class StartSessionSerializer(serializers.Serializer):
    task_id = serializers.IntegerField()
    completion_percentage = serializers.IntegerField(min_value=0, max_value=100, required=False, default=0)


class SwitchTaskSerializer(serializers.Serializer):
    next_task_id = serializers.IntegerField()
    completion_percentage = serializers.IntegerField(min_value=0, max_value=100)
    note = serializers.CharField(required=False, allow_blank=True, default="")


class CollaborationRequestSerializer(serializers.ModelSerializer):
    requester_username = serializers.CharField(source="requester.username", read_only=True)
    target_username = serializers.CharField(source="target.username", read_only=True)
    task_title = serializers.CharField(source="task.title", read_only=True)

    class Meta:
        model = CollaborationRequest
        fields = [
            "id", "requester_username", "target_username", "task_id", "task_title",
            "status", "message", "created_at", "responded_at",
        ]
        read_only_fields = ["id", "requester_username", "target_username", "task_title", "status", "created_at", "responded_at"]


class SendCollaborationRequestSerializer(serializers.Serializer):
    target_username = serializers.CharField()
    task_id = serializers.IntegerField()
    message = serializers.CharField(required=False, allow_blank=True, default="")


class TaskCollaboratorSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="member.username", read_only=True)
    full_name = serializers.CharField(source="member.user.full_name", read_only=True)

    class Meta:
        model = TaskCollaborator
        fields = ["id", "username", "full_name", "joined_at", "left_at", "is_active"]


class CollaborationActivityLogSerializer(serializers.ModelSerializer):
    actor_username = serializers.CharField(source="actor.username", read_only=True)

    class Meta:
        model = CollaborationActivityLog
        fields = ["id", "actor_username", "action_type", "metadata", "timestamp"]


class DeveloperStatusSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="membership.username", read_only=True)
    current_task = serializers.SerializerMethodField()
    last_seen = serializers.DateTimeField(read_only=True)

    class Meta:
        model = DeveloperStatus
        fields = ["username", "current_task", "last_seen"]

    def get_current_task(self, obj):
        if obj.current_session:
            task = obj.current_session.task
            collabs = TaskCollaborator.objects.filter(
                task=task, is_active=True
            ).exclude(member=obj.membership).select_related("member")
            return {
                "id": task.id,
                "title": task.title,
                "started_at": obj.current_session.started_at,
                "completion": task.completion_percentage,
                "collaborators": [c.member.username for c in collabs],
            }
        return None
