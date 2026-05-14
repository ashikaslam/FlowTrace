import random
from django.db import models


class QuickNote(models.Model):
    COLOR_YELLOW = "yellow"
    COLOR_GREEN = "green"
    COLOR_RED = "red"
    COLOR_BLUE = "blue"
    COLOR_CHOICES = [
        (COLOR_YELLOW, "Yellow"),
        (COLOR_GREEN, "Green"),
        (COLOR_RED, "Red"),
        (COLOR_BLUE, "Blue"),
    ]
    COLORS = [COLOR_YELLOW, COLOR_GREEN, COLOR_RED, COLOR_BLUE]

    NOTE_PERSONAL = "personal"
    NOTE_TEAM = "team"
    TYPE_CHOICES = [
        (NOTE_PERSONAL, "Personal"),
        (NOTE_TEAM, "Team"),
    ]

    workspace = models.ForeignKey(
        "workspaces.Workspace", on_delete=models.CASCADE, related_name="notes"
    )
    created_by = models.ForeignKey(
        "accounts.WorkspaceMembership", on_delete=models.CASCADE, related_name="notes"
    )
    content = models.TextField()
    color = models.CharField(max_length=10, choices=COLOR_CHOICES, default=COLOR_YELLOW)
    note_type = models.CharField(max_length=10, choices=TYPE_CHOICES, default=NOTE_PERSONAL)
    is_pinned = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["workspace", "note_type"]),
            models.Index(fields=["workspace", "created_by"]),
            models.Index(fields=["workspace", "is_pinned"]),
        ]
        ordering = ["-is_pinned", "-updated_at"]

    def save(self, *args, **kwargs):
        if not self.pk and self.color == self.COLOR_YELLOW:
            self.color = random.choice(self.COLORS)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Note by {self.created_by_id} [{self.workspace_id}]"
