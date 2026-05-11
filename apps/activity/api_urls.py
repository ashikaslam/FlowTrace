from django.urls import path
from .views import (
    StartSessionView, SwitchTaskView, StopSessionView,
    MyTimelineView, DeveloperTimelineView,
    WorkspaceLiveStatusView, MyCurrentStatusView,
    WorkspaceMemberSearchView, SendCollaborationRequestView,
    IncomingCollaborationRequestsView, RespondCollaborationRequestView,
    CancelCollaborationRequestView, TaskCollaboratorsView,
    TaskCollaborationLogsView, LeaveCollaborationView,
    MyCollaborationTimelineView, WorkspaceCollaborationsView,
    MyCollaborationHistoryView,
)

urlpatterns = [
    path("<str:workspace_slug>/start/", StartSessionView.as_view(), name="api-start-session"),
    path("<str:workspace_slug>/switch/", SwitchTaskView.as_view(), name="api-switch-task"),
    path("<str:workspace_slug>/stop/", StopSessionView.as_view(), name="api-stop-session"),
    path("<str:workspace_slug>/timeline/", MyTimelineView.as_view(), name="api-my-timeline"),
    path("<str:workspace_slug>/timeline/<str:username>/", DeveloperTimelineView.as_view(), name="api-dev-timeline"),
    path("<str:workspace_slug>/live/", WorkspaceLiveStatusView.as_view(), name="api-live-status"),
    path("<str:workspace_slug>/status/", MyCurrentStatusView.as_view(), name="api-my-status"),
    # Collaboration
    path("<str:workspace_slug>/collab/members/", WorkspaceMemberSearchView.as_view(), name="api-collab-members"),
    path("<str:workspace_slug>/collab/request/", SendCollaborationRequestView.as_view(), name="api-collab-request"),
    path("<str:workspace_slug>/collab/incoming/", IncomingCollaborationRequestsView.as_view(), name="api-collab-incoming"),
    path("<str:workspace_slug>/collab/history/", MyCollaborationHistoryView.as_view(), name="api-collab-history"),
    path("<str:workspace_slug>/collab/<int:request_id>/respond/", RespondCollaborationRequestView.as_view(), name="api-collab-respond"),
    path("<str:workspace_slug>/collab/<int:request_id>/cancel/", CancelCollaborationRequestView.as_view(), name="api-collab-cancel"),
    path("<str:workspace_slug>/collab/tasks/<int:task_id>/collaborators/", TaskCollaboratorsView.as_view(), name="api-task-collaborators"),
    path("<str:workspace_slug>/collab/tasks/<int:task_id>/logs/", TaskCollaborationLogsView.as_view(), name="api-task-collab-logs"),
    path("<str:workspace_slug>/collab/tasks/<int:task_id>/leave/", LeaveCollaborationView.as_view(), name="api-collab-leave"),
    path("<str:workspace_slug>/collab/my-timeline/", MyCollaborationTimelineView.as_view(), name="api-collab-my-timeline"),
    path("<str:workspace_slug>/collab/workspace/", WorkspaceCollaborationsView.as_view(), name="api-collab-workspace"),
]
