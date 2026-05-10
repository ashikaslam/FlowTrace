from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import Workspace
from .serializers import WorkspaceSerializer, WorkspaceCreateSerializer
from .permissions import IsWorkspaceMember
from apps.accounts.models import WorkspaceMembership


class WorkspaceListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        return WorkspaceCreateSerializer if self.request.method == "POST" else WorkspaceSerializer

    def get_queryset(self):
        return Workspace.objects.filter(
            memberships__user=self.request.user, memberships__is_active=True
        ).distinct()


class WorkspaceDetailView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated, IsWorkspaceMember]
    serializer_class = WorkspaceSerializer
    lookup_field = "slug"
    lookup_url_kwarg = "workspace_slug"
    queryset = Workspace.objects.all()


class WorkspaceStatsView(APIView):
    permission_classes = [IsAuthenticated, IsWorkspaceMember]

    def get(self, request, workspace_slug):
        from apps.tasks.models import Task
        from apps.activity.models import ActivitySession
        from django.utils import timezone
        from datetime import timedelta

        workspace = Workspace.objects.get(slug=workspace_slug)
        today = timezone.now().date()

        members = WorkspaceMembership.objects.filter(workspace=workspace, is_active=True)
        active_sessions = ActivitySession.objects.filter(
            task__workspace=workspace,
            ended_at__isnull=True,
        ).select_related("membership__user", "task")

        return Response({
            "total_members": members.count(),
            "active_now": active_sessions.count(),
            "total_tasks": Task.objects.filter(workspace=workspace).count(),
            "active_sessions": [
                {
                    "username": s.membership.username,
                    "task": s.task.title,
                    "started_at": s.started_at,
                }
                for s in active_sessions
            ],
        })
