from django.urls import path
from .views import (
    StartSessionView, SwitchTaskView, StopSessionView,
    MyTimelineView, DeveloperTimelineView,
    WorkspaceLiveStatusView, MyCurrentStatusView,
)

urlpatterns = [
    path("<str:workspace_slug>/start/", StartSessionView.as_view(), name="api-start-session"),
    path("<str:workspace_slug>/switch/", SwitchTaskView.as_view(), name="api-switch-task"),
    path("<str:workspace_slug>/stop/", StopSessionView.as_view(), name="api-stop-session"),
    path("<str:workspace_slug>/timeline/", MyTimelineView.as_view(), name="api-my-timeline"),
    path("<str:workspace_slug>/timeline/<str:username>/", DeveloperTimelineView.as_view(), name="api-dev-timeline"),
    path("<str:workspace_slug>/live/", WorkspaceLiveStatusView.as_view(), name="api-live-status"),
    path("<str:workspace_slug>/status/", MyCurrentStatusView.as_view(), name="api-my-status"),
]
