from django.urls import path
from .views import (
    TaskCommentListCreateView, MyMentionsView,
    MarkMentionReadView, MentionSuggestView,
)

urlpatterns = [
    path("<str:workspace_slug>/tasks/<int:task_id>/", TaskCommentListCreateView.as_view(), name="api-comments"),
    path("<str:workspace_slug>/mentions/", MyMentionsView.as_view(), name="api-mentions"),
    path("<str:workspace_slug>/mentions/<int:mention_id>/read/", MarkMentionReadView.as_view(), name="api-mention-read"),
    path("<str:workspace_slug>/suggest/", MentionSuggestView.as_view(), name="api-mention-suggest"),
]
