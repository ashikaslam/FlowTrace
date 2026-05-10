from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import RegisterView, RegisterWithWorkspaceView, WorkspaceLoginView, MeView, WorkspaceMembersView, CreateDeveloperView

urlpatterns = [
    path("register/", RegisterView.as_view(), name="api-register"),
    path("register-workspace/", RegisterWithWorkspaceView.as_view(), name="api-register-workspace"),
    path("login/", WorkspaceLoginView.as_view(), name="api-login"),
    path("token/refresh/", TokenRefreshView.as_view(), name="api-token-refresh"),
    path("me/", MeView.as_view(), name="api-me"),
    path("<str:workspace_slug>/members/", WorkspaceMembersView.as_view(), name="api-members"),
    path("<str:workspace_slug>/developers/create/", CreateDeveloperView.as_view(), name="api-create-developer"),
]
