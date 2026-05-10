from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import TaskComment, Mention
from .serializers import TaskCommentSerializer, MentionSerializer
from apps.workspaces.permissions import IsWorkspaceMember
from apps.accounts.models import WorkspaceMembership
from apps.tasks.models import Task


def get_membership(user, workspace_slug):
    return WorkspaceMembership.objects.get(
        user=user, workspace__slug=workspace_slug, is_active=True
    )


class TaskCommentListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated, IsWorkspaceMember]
    serializer_class = TaskCommentSerializer

    def get_queryset(self):
        return TaskComment.objects.filter(
            task__id=self.kwargs["task_id"],
            task__workspace__slug=self.kwargs["workspace_slug"],
        ).select_related("author").prefetch_related("mentions__mentioned_user")

    def perform_create(self, serializer):
        membership = get_membership(self.request.user, self.kwargs["workspace_slug"])
        task = Task.objects.get(
            id=self.kwargs["task_id"], workspace__slug=self.kwargs["workspace_slug"]
        )
        serializer.save(task=task, author=membership)


class MyMentionsView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, IsWorkspaceMember]
    serializer_class = MentionSerializer

    def get_queryset(self):
        membership = get_membership(self.request.user, self.kwargs["workspace_slug"])
        return Mention.objects.filter(mentioned_user=membership).select_related("comment")


class MarkMentionReadView(APIView):
    permission_classes = [IsAuthenticated, IsWorkspaceMember]

    def post(self, request, workspace_slug, mention_id):
        membership = get_membership(request.user, workspace_slug)
        Mention.objects.filter(id=mention_id, mentioned_user=membership).update(is_read=True)
        return Response({"status": "marked read"})


class MentionSuggestView(APIView):
    """Autocomplete @mention suggestions within workspace."""
    permission_classes = [IsAuthenticated, IsWorkspaceMember]

    def get(self, request, workspace_slug):
        q = request.query_params.get("q", "")
        members = WorkspaceMembership.objects.filter(
            workspace__slug=workspace_slug,
            username__icontains=q,
            is_active=True,
        ).values_list("username", flat=True)[:10]
        return Response(list(members))
