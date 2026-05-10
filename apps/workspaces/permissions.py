from rest_framework.permissions import BasePermission
from apps.accounts.models import WorkspaceMembership


def get_membership(user, workspace_slug):
    try:
        return WorkspaceMembership.objects.get(
            user=user, workspace__slug=workspace_slug, is_active=True
        )
    except WorkspaceMembership.DoesNotExist:
        return None


class IsWorkspaceMember(BasePermission):
    def has_permission(self, request, view):
        slug = view.kwargs.get("workspace_slug")
        return bool(slug and get_membership(request.user, slug))


class IsWorkspaceManager(BasePermission):
    def has_permission(self, request, view):
        slug = view.kwargs.get("workspace_slug")
        membership = get_membership(request.user, slug)
        return bool(membership and membership.role == WorkspaceMembership.ROLE_MANAGER)
