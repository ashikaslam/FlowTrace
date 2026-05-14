from django.urls import path
from .views import QuickNoteListCreateView, QuickNoteDetailView, QuickNotePinView

urlpatterns = [
    path("<str:workspace_slug>/", QuickNoteListCreateView.as_view(), name="api-notes"),
    path("<str:workspace_slug>/<int:pk>/", QuickNoteDetailView.as_view(), name="api-note-detail"),
    path("<str:workspace_slug>/<int:pk>/pin/", QuickNotePinView.as_view(), name="api-note-pin"),
]
