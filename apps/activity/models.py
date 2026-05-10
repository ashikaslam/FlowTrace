from django.db import models
from django.utils import timezone


class CollaborationRequest(models.Model):
    STATUS_PENDING = "pending"
    STATUS_ACCEPTED = "accepted"
    STATUS_REJECTED = "rejected"
    STATUS_CANCELLED = "cancelled"
    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_ACCEPTED, "Accepted"),
        (STATUS_REJECTED, "Rejected"),
        (STATUS_CANCELLED, "Cancelled"),
    ]

    requester = models.ForeignKey(
        "accounts.WorkspaceMembership", on_delete=models.CASCADE, related_name="sent_collab_requests"
    )
    target = models.ForeignKey(
        "accounts.WorkspaceMembership", on_delete=models.CASCADE, related_name="received_collab_requests"
    )
    task = models.ForeignKey(
        "tasks.Task", on_delete=models.CASCADE, related_name="collab_requests"
    )
    workspace = models.ForeignKey(
        "workspaces.Workspace", on_delete=models.CASCADE, related_name="collab_requests"
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    message = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    responded_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = [("requester", "target", "task")]
        indexes = [
            models.Index(fields=["target", "status"]),
            models.Index(fields=["task", "status"]),
        ]
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.requester.username} → {self.target.username} on '{self.task.title}' [{self.status}]"


class TaskCollaborator(models.Model):
    task = models.ForeignKey(
        "tasks.Task", on_delete=models.CASCADE, related_name="collaborators"
    )
    member = models.ForeignKey(
        "accounts.WorkspaceMembership", on_delete=models.CASCADE, related_name="collaborations"
    )
    joined_at = models.DateTimeField(default=timezone.now)
    left_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = [("task", "member")]
        indexes = [models.Index(fields=["task", "is_active"])]
        ordering = ["joined_at"]

    def __str__(self):
        return f"{self.member.username} collaborating on '{self.task.title}'"


class CollaborationActivityLog(models.Model):
    ACTION_REQUEST_SENT = "request_sent"
    ACTION_REQUEST_ACCEPTED = "request_accepted"
    ACTION_REQUEST_REJECTED = "request_rejected"
    ACTION_REQUEST_CANCELLED = "request_cancelled"
    ACTION_COLLAB_STARTED = "collab_started"
    ACTION_COLLAB_ENDED = "collab_ended"
    ACTION_CHOICES = [
        (ACTION_REQUEST_SENT, "Request Sent"),
        (ACTION_REQUEST_ACCEPTED, "Request Accepted"),
        (ACTION_REQUEST_REJECTED, "Request Rejected"),
        (ACTION_REQUEST_CANCELLED, "Request Cancelled"),
        (ACTION_COLLAB_STARTED, "Collaboration Started"),
        (ACTION_COLLAB_ENDED, "Collaboration Ended"),
    ]

    task = models.ForeignKey(
        "tasks.Task", on_delete=models.CASCADE, related_name="collab_logs"
    )
    actor = models.ForeignKey(
        "accounts.WorkspaceMembership", on_delete=models.CASCADE, related_name="collab_logs"
    )
    action_type = models.CharField(max_length=30, choices=ACTION_CHOICES)
    metadata = models.JSONField(default=dict, blank=True)
    timestamp = models.DateTimeField(default=timezone.now)

    class Meta:
        indexes = [models.Index(fields=["task", "timestamp"])]
        ordering = ["-timestamp"]

    def __str__(self):
        return f"{self.actor.username} {self.action_type} on '{self.task.title}'"


class ActivitySession(models.Model):
    """Represents one continuous work session on a task."""

    membership = models.ForeignKey(
        "accounts.WorkspaceMembership", on_delete=models.CASCADE, related_name="sessions"
    )
    task = models.ForeignKey(
        "tasks.Task", on_delete=models.CASCADE, related_name="sessions"
    )
    started_at = models.DateTimeField(default=timezone.now)
    ended_at = models.DateTimeField(null=True, blank=True)
    completion_at_start = models.PositiveSmallIntegerField(default=0)
    completion_at_end = models.PositiveSmallIntegerField(null=True, blank=True)
    switch_note = models.TextField(blank=True)  # optional note when switching away

    class Meta:
        indexes = [
            models.Index(fields=["membership", "started_at"]),
            models.Index(fields=["task", "started_at"]),
        ]
        ordering = ["-started_at"]

    @property
    def duration_seconds(self):
        end = self.ended_at or timezone.now()
        return int((end - self.started_at).total_seconds())

    def close(self, completion_percentage, note=""):
        self.ended_at = timezone.now()
        self.completion_at_end = completion_percentage
        self.switch_note = note
        self.save(update_fields=["ended_at", "completion_at_end", "switch_note"])

    def __str__(self):
        return f"{self.membership.username} → {self.task.title} @ {self.started_at:%Y-%m-%d %H:%M}"


class DeveloperStatus(models.Model):
    """Tracks the current active session per developer (one row per membership)."""

    membership = models.OneToOneField(
        "accounts.WorkspaceMembership", on_delete=models.CASCADE, related_name="status"
    )
    current_session = models.ForeignKey(
        ActivitySession, on_delete=models.SET_NULL, null=True, blank=True
    )
    last_seen = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.membership.username} status"
