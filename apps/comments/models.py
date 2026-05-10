from django.db import models
import re


class TaskComment(models.Model):
    task = models.ForeignKey(
        "tasks.Task", on_delete=models.CASCADE, related_name="comments"
    )
    author = models.ForeignKey(
        "accounts.WorkspaceMembership", on_delete=models.CASCADE, related_name="comments"
    )
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["created_at"]

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self._process_mentions()

    def _process_mentions(self):
        usernames = set(re.findall(r"@(\w+)", self.body))
        for username in usernames:
            try:
                mentioned = self.task.workspace.memberships.get(username=username, is_active=True)
                Mention.objects.get_or_create(comment=self, mentioned_user=mentioned)
            except Exception:
                pass

    def __str__(self):
        return f"Comment by {self.author.username} on {self.task.title}"


class Mention(models.Model):
    comment = models.ForeignKey(TaskComment, on_delete=models.CASCADE, related_name="mentions")
    mentioned_user = models.ForeignKey(
        "accounts.WorkspaceMembership", on_delete=models.CASCADE, related_name="mentions"
    )
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [("comment", "mentioned_user")]

    def __str__(self):
        return f"@{self.mentioned_user.username} in comment {self.comment.id}"
