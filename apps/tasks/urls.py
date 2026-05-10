from django.urls import path
from . import page_views

urlpatterns = [
    path("<str:workspace_slug>/", page_views.task_list, name="task-list"),
    path("<str:workspace_slug>/<int:task_id>/", page_views.task_detail, name="task-detail"),
]
