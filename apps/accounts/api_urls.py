from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import RegisterView, RegisterWithWorkspaceView, WorkspaceLoginView, MeView, WorkspaceMembersView, CreateDeveloperView, UpdateProfileView, AvatarUploadView

urlpatterns = [
    path("register/", RegisterView.as_view(), name="api-register"),
    path("register-workspace/", RegisterWithWorkspaceView.as_view(), name="api-register-workspace"),
    path("login/", WorkspaceLoginView.as_view(), name="api-login"),
    path("token/refresh/", TokenRefreshView.as_view(), name="api-token-refresh"),
    path("me/", MeView.as_view(), name="api-me"),
    path("<str:workspace_slug>/members/", WorkspaceMembersView.as_view(), name="api-members"),
    path("<str:workspace_slug>/developers/create/", CreateDeveloperView.as_view(), name="api-create-developer"),
    path("<str:workspace_slug>/profile/update/", UpdateProfileView.as_view(), name="api-profile-update"),
    path("avatar/upload/", AvatarUploadView.as_view(), name="api-avatar-upload"),
]
