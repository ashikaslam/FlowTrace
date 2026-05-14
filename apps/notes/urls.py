from django.urls import path
from .page_views import note_detail

urlpatterns = [
    path("<str:workspace_slug>/<int:note_id>/", note_detail, name="note-detail"),
]
