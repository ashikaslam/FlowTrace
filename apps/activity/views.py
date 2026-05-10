from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics

from .models import ActivitySession, DeveloperStatus
from .serializers import (
    ActivitySessionSerializer, StartSessionSerializer,
    SwitchTaskSerializer, DeveloperStatusSerializer,
)
from .services import start_session, switch_task, stop_session
from apps.workspaces.permissions import IsWorkspaceMember
from apps.accounts.models import WorkspaceMembership


def get_membership(user, workspace_slug):
    return WorkspaceMembership.objects.get(
        user=user, workspace__slug=workspace_slug, is_active=True
    )


class StartSessionView(APIView):
    permission_classes = [IsAuthenticated, IsWorkspaceMember]

    def post(self, request, workspace_slug):
        serializer = StartSessionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        membership = get_membership(request.user, workspace_slug)
        session = start_session(membership, serializer.validated_data["task_id"])
        return Response(ActivitySessionSerializer(session).data, status=201)


class SwitchTaskView(APIView):
    permission_classes = [IsAuthenticated, IsWorkspaceMember]

    def post(self, request, workspace_slug):
        serializer = SwitchTaskSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        membership = get_membership(request.user, workspace_slug)
        d = serializer.validated_data
        session = switch_task(membership, d["next_task_id"], d["completion_percentage"], d.get("note", ""))
        return Response(ActivitySessionSerializer(session).data, status=201)


class StopSessionView(APIView):
    permission_classes = [IsAuthenticated, IsWorkspaceMember]

    def post(self, request, workspace_slug):
        membership = get_membership(request.user, workspace_slug)
        completion = request.data.get("completion_percentage", 0)
        note = request.data.get("note", "")
        stop_session(membership, completion, note)
        return Response({"status": "stopped"})


class MyTimelineView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, IsWorkspaceMember]
    serializer_class = ActivitySessionSerializer

    def get_queryset(self):
        membership = get_membership(self.request.user, self.kwargs["workspace_slug"])
        qs = ActivitySession.objects.filter(membership=membership).select_related("task")
        date = self.request.query_params.get("date")
        if date:
            qs = qs.filter(started_at__date=date)
        return qs


class DeveloperTimelineView(generics.ListAPIView):
    """Manager view: see any developer's timeline."""
    permission_classes = [IsAuthenticated, IsWorkspaceMember]
    serializer_class = ActivitySessionSerializer

    def get_queryset(self):
        workspace_slug = self.kwargs["workspace_slug"]
        username = self.kwargs["username"]
        qs = ActivitySession.objects.filter(
            membership__workspace__slug=workspace_slug,
            membership__username=username,
        ).select_related("task")
        date = self.request.query_params.get("date")
        if date:
            qs = qs.filter(started_at__date=date)
        return qs


class WorkspaceLiveStatusView(APIView):
    """Real-time status of all developers in a workspace."""
    permission_classes = [IsAuthenticated, IsWorkspaceMember]

    def get(self, request, workspace_slug):
        statuses = DeveloperStatus.objects.filter(
            membership__workspace__slug=workspace_slug,
            membership__is_active=True,
        ).select_related("membership", "current_session__task")
        return Response(DeveloperStatusSerializer(statuses, many=True).data)


class MyCurrentStatusView(APIView):
    permission_classes = [IsAuthenticated, IsWorkspaceMember]

    def get(self, request, workspace_slug):
        membership = get_membership(request.user, workspace_slug)
        status, _ = DeveloperStatus.objects.get_or_create(membership=membership)
        return Response(DeveloperStatusSerializer(status).data)
