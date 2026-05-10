from django.urls import path
from . import page_views

urlpatterns = [
    path("<str:workspace_slug>/", page_views.manager_dashboard, name="manager-dashboard"),
    path("<str:workspace_slug>/dev/", page_views.developer_dashboard, name="developer-dashboard"),
    path("<str:workspace_slug>/settings/", page_views.workspace_settings, name="workspace-settings"),
]
