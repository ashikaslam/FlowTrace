from django.urls import path
from .views import WorkspaceListCreateView, WorkspaceDetailView, WorkspaceStatsView

urlpatterns = [
    path("", WorkspaceListCreateView.as_view(), name="api-workspaces"),
    path("<str:workspace_slug>/", WorkspaceDetailView.as_view(), name="api-workspace-detail"),
    path("<str:workspace_slug>/stats/", WorkspaceStatsView.as_view(), name="api-workspace-stats"),
]
