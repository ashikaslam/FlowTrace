from django.db import models
from django.utils.text import slugify
import secrets
import string


def generate_unique_slug(name):
    base = slugify(name)[:20]
    suffix = "".join(secrets.choice(string.ascii_lowercase + string.digits) for _ in range(4))
    return f"{base}-{suffix}"


class Workspace(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=60, unique=True)
    owner = models.ForeignKey(
        "accounts.User", on_delete=models.CASCADE, related_name="owned_workspaces"
    )
    description = models.TextField(blank=True)
    logo = models.ImageField(upload_to="workspace_logos/", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        indexes = [models.Index(fields=["slug"])]

    def save(self, *args, **kwargs):
        if not self.slug:
            slug = generate_unique_slug(self.name)
            while Workspace.objects.filter(slug=slug).exists():
                slug = generate_unique_slug(self.name)
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.slug})"
