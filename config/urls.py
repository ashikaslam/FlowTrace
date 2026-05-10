from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    # Frontend page routes
    path("", include("apps.accounts.urls")),
    path("dashboard/", include("apps.workspaces.urls")),
    path("tasks/", include("apps.tasks.urls")),
    path("activity/", include("apps.activity.urls")),
    # REST API routes
    path("api/auth/", include("apps.accounts.api_urls")),
    path("api/workspaces/", include("apps.workspaces.api_urls")),
    path("api/tasks/", include("apps.tasks.api_urls")),
    path("api/activity/", include("apps.activity.api_urls")),
    path("api/comments/", include("apps.comments.api_urls")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
