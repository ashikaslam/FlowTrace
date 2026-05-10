from django.urls import path
from . import page_views

urlpatterns = [
    path("<str:workspace_slug>/", page_views.activity_timeline, name="activity-timeline"),
]
