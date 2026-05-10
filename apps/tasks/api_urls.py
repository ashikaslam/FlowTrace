from django.urls import path
from .views import TaskListCreateView, TaskDetailView, TaskAttachmentView

urlpatterns = [
    path("<str:workspace_slug>/", TaskListCreateView.as_view(), name="api-tasks"),
    path("<str:workspace_slug>/<int:pk>/", TaskDetailView.as_view(), name="api-task-detail"),
    path("<str:workspace_slug>/<int:task_id>/attachments/", TaskAttachmentView.as_view(), name="api-task-attachments"),
]
