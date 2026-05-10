from rest_framework import serializers
from .models import Workspace
from apps.accounts.models import WorkspaceMembership


class WorkspaceSerializer(serializers.ModelSerializer):
    member_count = serializers.SerializerMethodField()

    class Meta:
        model = Workspace
        fields = ["id", "name", "slug", "description", "logo", "created_at", "member_count"]
        read_only_fields = ["slug", "created_at"]

    def get_member_count(self, obj):
        return obj.memberships.filter(is_active=True).count()


class WorkspaceCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Workspace
        fields = ["name", "description", "logo"]

    def create(self, validated_data):
        user = self.context["request"].user
        workspace = Workspace.objects.create(owner=user, **validated_data)
        # Auto-create manager membership for creator
        WorkspaceMembership.objects.create(
            user=user,
            workspace=workspace,
            role=WorkspaceMembership.ROLE_MANAGER,
            username=user.email.split("@")[0],
        )
        return workspace
