from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics
from django.utils import timezone
from django.db import transaction

from .models import ActivitySession, DeveloperStatus, CollaborationRequest, TaskCollaborator, CollaborationActivityLog
from .serializers import (
    ActivitySessionSerializer, StartSessionSerializer,
    SwitchTaskSerializer, DeveloperStatusSerializer,
    CollaborationRequestSerializer, SendCollaborationRequestSerializer,
    TaskCollaboratorSerializer, CollaborationActivityLogSerializer,
)
from .services import start_session, switch_task, stop_session
from apps.workspaces.permissions import IsWorkspaceMember
from apps.accounts.models import WorkspaceMembership
from apps.tasks.models import Task


def get_membership(user, workspace_slug):
    return WorkspaceMembership.objects.get(
        user=user, workspace__slug=workspace_slug, is_active=True
    )


def _apply_date_filter(qs, params):
    """Apply date or date range filter to a queryset on started_at."""
    date = params.get("date")
    date_from = params.get("date_from")
    date_to = params.get("date_to")
    if date:
        qs = qs.filter(started_at__date=date)
    else:
        if date_from:
            qs = qs.filter(started_at__date__gte=date_from)
        if date_to:
            qs = qs.filter(started_at__date__lte=date_to)
    return qs


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
        return _apply_date_filter(qs, self.request.query_params)


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
        return _apply_date_filter(qs, self.request.query_params)


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


# ── Collaboration ──────────────────────────────────────────────────────────────

class WorkspaceMemberSearchView(APIView):
    """Search workspace members by username for collaboration selection."""
    permission_classes = [IsAuthenticated, IsWorkspaceMember]

    def get(self, request, workspace_slug):
        q = request.query_params.get("q", "").strip()
        membership = get_membership(request.user, workspace_slug)
        qs = WorkspaceMembership.objects.filter(
            workspace__slug=workspace_slug, is_active=True
        ).exclude(id=membership.id).select_related("user")
        if q:
            qs = qs.filter(username__icontains=q) | WorkspaceMembership.objects.filter(
                workspace__slug=workspace_slug, is_active=True, user__full_name__icontains=q
            ).exclude(id=membership.id).select_related("user")
            qs = qs.distinct()
        results = [{"username": m.username, "full_name": m.user.full_name, "avatar_url": m.user.avatar_url} for m in qs[:50]]
        return Response(results)


class SendCollaborationRequestView(APIView):
    permission_classes = [IsAuthenticated, IsWorkspaceMember]

    def post(self, request, workspace_slug):
        serializer = SendCollaborationRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        d = serializer.validated_data

        requester = get_membership(request.user, workspace_slug)
        try:
            target = WorkspaceMembership.objects.get(
                workspace__slug=workspace_slug, username=d["target_username"], is_active=True
            )
        except WorkspaceMembership.DoesNotExist:
            return Response({"error": "Developer not found in this workspace."}, status=404)

        if target == requester:
            return Response({"error": "Cannot request collaboration with yourself."}, status=400)

        try:
            task = Task.objects.get(id=d["task_id"], workspace__slug=workspace_slug)
        except Task.DoesNotExist:
            return Response({"error": "Task not found."}, status=404)

        collab_req, created = CollaborationRequest.objects.get_or_create(
            requester=requester, target=target, task=task,
            defaults={"workspace": task.workspace, "message": d["message"], "status": CollaborationRequest.STATUS_PENDING},
        )
        if not created:
            if collab_req.status == CollaborationRequest.STATUS_PENDING:
                return Response({"error": "Request already pending."}, status=400)
            # Re-open a previously closed request
            collab_req.status = CollaborationRequest.STATUS_PENDING
            collab_req.message = d["message"]
            collab_req.responded_at = None
            collab_req.save(update_fields=["status", "message", "responded_at"])

        CollaborationActivityLog.objects.create(
            task=task, actor=requester,
            action_type=CollaborationActivityLog.ACTION_REQUEST_SENT,
            metadata={"target": target.username},
        )
        return Response(CollaborationRequestSerializer(collab_req).data, status=201)


class IncomingCollaborationRequestsView(generics.ListAPIView):
    """Pending requests received by the current developer."""
    permission_classes = [IsAuthenticated, IsWorkspaceMember]
    serializer_class = CollaborationRequestSerializer

    def get_queryset(self):
        membership = get_membership(self.request.user, self.kwargs["workspace_slug"])
        return CollaborationRequest.objects.filter(
            target=membership, status=CollaborationRequest.STATUS_PENDING
        ).select_related("requester", "task")


class RespondCollaborationRequestView(APIView):
    permission_classes = [IsAuthenticated, IsWorkspaceMember]

    @transaction.atomic
    def post(self, request, workspace_slug, request_id):
        membership = get_membership(request.user, workspace_slug)
        try:
            collab_req = CollaborationRequest.objects.select_related("task", "requester").get(
                id=request_id, target=membership, status=CollaborationRequest.STATUS_PENDING
            )
        except CollaborationRequest.DoesNotExist:
            return Response({"error": "Request not found."}, status=404)

        action = request.data.get("action")
        if action not in ("accept", "reject"):
            return Response({"error": "action must be 'accept' or 'reject'."}, status=400)

        collab_req.status = CollaborationRequest.STATUS_ACCEPTED if action == "accept" else CollaborationRequest.STATUS_REJECTED
        collab_req.responded_at = timezone.now()
        collab_req.save(update_fields=["status", "responded_at"])

        log_action = CollaborationActivityLog.ACTION_REQUEST_ACCEPTED if action == "accept" else CollaborationActivityLog.ACTION_REQUEST_REJECTED
        CollaborationActivityLog.objects.create(
            task=collab_req.task, actor=membership,
            action_type=log_action,
            metadata={"requester": collab_req.requester.username},
        )

        if action == "accept":
            collaborator, created = TaskCollaborator.objects.get_or_create(
                task=collab_req.task, member=membership,
                defaults={"is_active": True},
            )
            if not created and not collaborator.is_active:
                collaborator.is_active = True
                collaborator.left_at = None
                collaborator.joined_at = timezone.now()
                collaborator.save(update_fields=["is_active", "left_at", "joined_at"])

            CollaborationActivityLog.objects.create(
                task=collab_req.task, actor=membership,
                action_type=CollaborationActivityLog.ACTION_COLLAB_STARTED,
                metadata={"with": collab_req.requester.username},
            )

        return Response(CollaborationRequestSerializer(collab_req).data)


class CancelCollaborationRequestView(APIView):
    permission_classes = [IsAuthenticated, IsWorkspaceMember]

    def post(self, request, workspace_slug, request_id):
        membership = get_membership(request.user, workspace_slug)
        try:
            collab_req = CollaborationRequest.objects.get(
                id=request_id, requester=membership, status=CollaborationRequest.STATUS_PENDING
            )
        except CollaborationRequest.DoesNotExist:
            return Response({"error": "Request not found."}, status=404)

        collab_req.status = CollaborationRequest.STATUS_CANCELLED
        collab_req.responded_at = timezone.now()
        collab_req.save(update_fields=["status", "responded_at"])

        CollaborationActivityLog.objects.create(
            task=collab_req.task, actor=membership,
            action_type=CollaborationActivityLog.ACTION_REQUEST_CANCELLED,
            metadata={"target": collab_req.target.username},
        )
        return Response({"status": "cancelled"})


class TaskCollaboratorsView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, IsWorkspaceMember]
    serializer_class = TaskCollaboratorSerializer

    def get_queryset(self):
        return TaskCollaborator.objects.filter(
            task_id=self.kwargs["task_id"],
            task__workspace__slug=self.kwargs["workspace_slug"],
        ).select_related("member", "member__user")


class TaskCollaborationLogsView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, IsWorkspaceMember]
    serializer_class = CollaborationActivityLogSerializer

    def get_queryset(self):
        return CollaborationActivityLog.objects.filter(
            task_id=self.kwargs["task_id"],
            task__workspace__slug=self.kwargs["workspace_slug"],
        ).select_related("actor")


class LeaveCollaborationView(APIView):
    permission_classes = [IsAuthenticated, IsWorkspaceMember]

    def post(self, request, workspace_slug, task_id):
        membership = get_membership(request.user, workspace_slug)
        try:
            collaborator = TaskCollaborator.objects.get(
                task_id=task_id, task__workspace__slug=workspace_slug,
                member=membership, is_active=True,
            )
        except TaskCollaborator.DoesNotExist:
            return Response({"error": "Not an active collaborator on this task."}, status=404)

        collaborator.is_active = False
        collaborator.left_at = timezone.now()
        collaborator.save(update_fields=["is_active", "left_at"])

        CollaborationActivityLog.objects.create(
            task_id=task_id, actor=membership,
            action_type=CollaborationActivityLog.ACTION_COLLAB_ENDED,
            metadata={},
        )
        return Response({"status": "left"})


class TaskMemberCollabStatusView(APIView):
    """Returns collab status of all workspace members for a specific task."""
    permission_classes = [IsAuthenticated, IsWorkspaceMember]

    def get(self, request, workspace_slug, task_id):
        membership = get_membership(request.user, workspace_slug)
        members = WorkspaceMembership.objects.filter(
            workspace__slug=workspace_slug, is_active=True
        ).exclude(id=membership.id).select_related("user")

        # Active collaborators
        active_collabs = set(
            TaskCollaborator.objects.filter(task_id=task_id, is_active=True)
            .values_list("member_id", flat=True)
        )
        # Latest request per target
        latest_requests = {}
        for req in CollaborationRequest.objects.filter(
            requester=membership, task_id=task_id
        ).order_by("-created_at"):
            if req.target_id not in latest_requests:
                latest_requests[req.target_id] = req.status

        result = {}
        for m in members:
            if m.id in active_collabs:
                result[m.username] = "collaborating"
            elif latest_requests.get(m.id) == CollaborationRequest.STATUS_PENDING:
                result[m.username] = "pending"
            elif latest_requests.get(m.id) == CollaborationRequest.STATUS_REJECTED:
                result[m.username] = "rejected"
            else:
                result[m.username] = "none"
        return Response(result)


class MyCollaborationHistoryView(APIView):
    """All collaboration requests involving the current developer (sent + received, all statuses)."""
    permission_classes = [IsAuthenticated, IsWorkspaceMember]

    def get(self, request, workspace_slug):
        membership = get_membership(request.user, workspace_slug)
        sent = CollaborationRequest.objects.filter(
            requester=membership, workspace__slug=workspace_slug
        ).select_related("target", "task").order_by("-created_at")
        received = CollaborationRequest.objects.filter(
            target=membership, workspace__slug=workspace_slug
        ).exclude(status=CollaborationRequest.STATUS_PENDING).select_related("requester", "task").order_by("-created_at")

        def fmt(r, direction):
            return {
                "id": r.id,
                "direction": direction,
                "other_username": r.target.username if direction == "sent" else r.requester.username,
                "task_id": r.task_id,
                "task_title": r.task.title,
                "status": r.status,
                "message": r.message,
                "created_at": r.created_at,
                "responded_at": r.responded_at,
            }

        history = [fmt(r, "sent") for r in sent] + [fmt(r, "received") for r in received]
        history.sort(key=lambda x: x["created_at"], reverse=True)
        return Response(history)


class MyCollaborationTimelineView(generics.ListAPIView):
    """Sessions on tasks where the current user is a collaborator (not the owner)."""
    permission_classes = [IsAuthenticated, IsWorkspaceMember]
    serializer_class = ActivitySessionSerializer

    def get_queryset(self):
        membership = get_membership(self.request.user, self.kwargs["workspace_slug"])
        collab_task_ids = TaskCollaborator.objects.filter(
            member=membership
        ).values_list("task_id", flat=True)
        qs = ActivitySession.objects.filter(
            task_id__in=collab_task_ids,
            task__workspace__slug=self.kwargs["workspace_slug"],
        ).select_related("task", "membership")
        return _apply_date_filter(qs, self.request.query_params)


class WorkspaceCollaborationsView(APIView):
    """Manager view: all active collaborative tasks in the workspace."""
    permission_classes = [IsAuthenticated, IsWorkspaceMember]

    def get(self, request, workspace_slug):
        # Tasks that have more than one active collaborator or have any TaskCollaborator
        active_collabs = TaskCollaborator.objects.filter(
            task__workspace__slug=workspace_slug,
            is_active=True,
        ).select_related("task", "member", "member__user")

        # Group by task
        tasks = {}
        for c in active_collabs:
            tid = c.task_id
            if tid not in tasks:
                tasks[tid] = {"task_id": tid, "task_title": c.task.title, "collaborators": [], "since": c.joined_at}
            tasks[tid]["collaborators"].append({"username": c.member.username, "full_name": c.member.user.full_name, "joined_at": c.joined_at})
            if c.joined_at < tasks[tid]["since"]:
                tasks[tid]["since"] = c.joined_at

        return Response(list(tasks.values()))
