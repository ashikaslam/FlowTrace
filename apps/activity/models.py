from django.db import models
from django.utils import timezone


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
