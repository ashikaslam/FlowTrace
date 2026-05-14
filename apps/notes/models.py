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
    title = models.CharField(max_length=200)
    content = models.TextField(blank=True)
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

    def __str__(self):
        return f"{self.title} [{self.workspace.slug}]"
