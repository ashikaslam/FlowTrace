from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser

from .models import Task, TaskAttachment
from .serializers import TaskSerializer, TaskCreateSerializer, TaskUpdateSerializer, TaskAttachmentSerializer
from apps.workspaces.permissions import IsWorkspaceMember
from apps.accounts.models import WorkspaceMembership


def get_membership(user, workspace_slug):
    return WorkspaceMembership.objects.get(
        user=user, workspace__slug=workspace_slug, is_active=True
    )


class TaskListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated, IsWorkspaceMember]

    def get_serializer_class(self):
        return TaskCreateSerializer if self.request.method == "POST" else TaskSerializer

    def get_queryset(self):
        qs = Task.objects.filter(
            workspace__slug=self.kwargs["workspace_slug"]
        ).select_related("created_by", "workspace")

        status_filter = self.request.query_params.get("status")
        if status_filter:
            qs = qs.filter(status=status_filter)

        # Developers only see their own tasks
        membership = WorkspaceMembership.objects.get(
            user=self.request.user, workspace__slug=self.kwargs["workspace_slug"]
        )
        if membership.role == WorkspaceMembership.ROLE_DEVELOPER:
            qs = qs.filter(created_by=membership)

        return qs

    def perform_create(self, serializer):
        membership = get_membership(self.request.user, self.kwargs["workspace_slug"])
        from apps.workspaces.models import Workspace
        workspace = Workspace.objects.get(slug=self.kwargs["workspace_slug"])
        serializer.save(workspace=workspace, created_by=membership)


class TaskDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated, IsWorkspaceMember]
    serializer_class = TaskSerializer

    def get_serializer_class(self):
        if self.request.method in ["PUT", "PATCH"]:
            return TaskUpdateSerializer
        return TaskSerializer

    def get_queryset(self):
        return Task.objects.filter(workspace__slug=self.kwargs["workspace_slug"])


class TaskAttachmentView(APIView):
    permission_classes = [IsAuthenticated, IsWorkspaceMember]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, workspace_slug, task_id):
        task = Task.objects.get(id=task_id, workspace__slug=workspace_slug)
        membership = get_membership(request.user, workspace_slug)
        file = request.FILES.get("file")
        if not file:
            return Response({"error": "No file provided."}, status=400)
        attachment = TaskAttachment.objects.create(
            task=task, uploaded_by=membership,
            file=file, filename=file.name,
        )
        return Response(TaskAttachmentSerializer(attachment).data, status=201)
