from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import QuickNote
from .serializers import QuickNoteSerializer, QuickNoteWriteSerializer
from apps.workspaces.permissions import IsWorkspaceMember, IsWorkspaceManager, get_membership


class QuickNoteListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated, IsWorkspaceMember]

    def get_serializer_class(self):
        return QuickNoteWriteSerializer if self.request.method == "POST" else QuickNoteSerializer

    def get_queryset(self):
        membership = get_membership(self.request.user, self.kwargs["workspace_slug"])
        # Developers see their own personal notes + all team notes
        # Managers see everything
        if membership.role == membership.ROLE_DEVELOPER:
            from django.db.models import Q
            return QuickNote.objects.filter(
                workspace__slug=self.kwargs["workspace_slug"]
            ).filter(
                Q(note_type=QuickNote.NOTE_PERSONAL, created_by=membership) |
                Q(note_type=QuickNote.NOTE_TEAM)
            ).select_related("created_by")
        return QuickNote.objects.filter(
            workspace__slug=self.kwargs["workspace_slug"]
        ).select_related("created_by")

    def perform_create(self, serializer):
        from apps.workspaces.models import Workspace
        membership = get_membership(self.request.user, self.kwargs["workspace_slug"])
        workspace = Workspace.objects.get(slug=self.kwargs["workspace_slug"])
        # Developers can only create personal notes
        note_type = serializer.validated_data.get("note_type", QuickNote.NOTE_PERSONAL)
        if membership.role == membership.ROLE_DEVELOPER:
            note_type = QuickNote.NOTE_PERSONAL
        serializer.save(workspace=workspace, created_by=membership, note_type=note_type)


class QuickNoteDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated, IsWorkspaceMember]

    def get_serializer_class(self):
        if self.request.method in ["PUT", "PATCH"]:
            return QuickNoteWriteSerializer
        return QuickNoteSerializer

    def get_queryset(self):
        return QuickNote.objects.filter(
            workspace__slug=self.kwargs["workspace_slug"]
        ).select_related("created_by")

    def check_object_permissions(self, request, obj):
        super().check_object_permissions(request, obj)
        if request.method in ["PUT", "PATCH", "DELETE"]:
            membership = get_membership(request.user, self.kwargs["workspace_slug"])
            # Owner can always edit/delete their own note
            # Manager can also delete team notes
            is_owner = obj.created_by == membership
            is_manager = membership.role == membership.ROLE_MANAGER
            if not is_owner and not (is_manager and obj.note_type == QuickNote.NOTE_TEAM):
                from rest_framework.exceptions import PermissionDenied
                raise PermissionDenied("You do not have permission to modify this note.")


class QuickNotePinView(APIView):
    permission_classes = [IsAuthenticated, IsWorkspaceMember]

    def post(self, request, workspace_slug, pk):
        membership = get_membership(request.user, workspace_slug)
        try:
            note = QuickNote.objects.get(pk=pk, workspace__slug=workspace_slug)
        except QuickNote.DoesNotExist:
            return Response({"error": "Note not found."}, status=404)
        # Only owner or manager can pin
        if note.created_by != membership and membership.role != membership.ROLE_MANAGER:
            return Response({"error": "Permission denied."}, status=403)
        note.is_pinned = not note.is_pinned
        note.save(update_fields=["is_pinned"])
        return Response({"is_pinned": note.is_pinned})
