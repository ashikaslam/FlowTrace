from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenRefreshView

from .models import User, WorkspaceMembership
from .serializers import (
    RegisterSerializer, UserSerializer,
    WorkspaceTokenSerializer, MembershipSerializer, CreateDeveloperSerializer,
)
from apps.workspaces.models import Workspace
from apps.workspaces.permissions import IsWorkspaceManager
import secrets
import string


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]


class RegisterWithWorkspaceView(APIView):
    """Single endpoint: create user + workspace + membership, return JWT."""
    permission_classes = [AllowAny]

    def post(self, request):
        from apps.workspaces.models import Workspace
        from apps.workspaces.serializers import WorkspaceCreateSerializer
        from rest_framework_simplejwt.tokens import RefreshToken

        email = request.data.get("email", "").strip()
        full_name = request.data.get("full_name", "").strip()
        password = request.data.get("password", "")
        workspace_name = request.data.get("workspace_name", "").strip()

        # Validate
        if not all([email, full_name, password, workspace_name]):
            return Response({"error": "All fields are required."}, status=400)
        if User.objects.filter(email=email).exists():
            return Response({"email": ["Email already registered."]}, status=400)
        if len(password) < 8:
            return Response({"password": ["Password must be at least 8 characters."]}, status=400)

        # Create user
        user = User.objects.create_user(email=email, full_name=full_name, password=password)

        # Create workspace (slug auto-generated)
        workspace = Workspace.objects.create(name=workspace_name, owner=user)

        # Auto-derive manager username from email prefix
        base_username = email.split("@")[0][:50]
        username = base_username
        suffix = 1
        while WorkspaceMembership.objects.filter(workspace=workspace, username=username).exists():
            username = f"{base_username}{suffix}"
            suffix += 1

        WorkspaceMembership.objects.create(
            user=user,
            workspace=workspace,
            role=WorkspaceMembership.ROLE_MANAGER,
            username=username,
        )

        # Issue JWT
        refresh = RefreshToken.for_user(user)
        refresh["workspace_id"] = workspace.id
        refresh["workspace_slug"] = workspace.slug
        refresh["role"] = WorkspaceMembership.ROLE_MANAGER
        refresh["username"] = username

        return Response({
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "workspace_slug": workspace.slug,
            "workspace_name": workspace.name,
            "username": username,
            "role": WorkspaceMembership.ROLE_MANAGER,
            "login_url": f"/workspace/{workspace.slug}/login/",
        }, status=201)


class WorkspaceLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = WorkspaceTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data)


class MeView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class WorkspaceMembersView(generics.ListAPIView):
    serializer_class = MembershipSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        slug = self.kwargs["workspace_slug"]
        return WorkspaceMembership.objects.filter(
            workspace__slug=slug, is_active=True
        ).select_related("user")


class CreateDeveloperView(APIView):
    permission_classes = [IsAuthenticated, IsWorkspaceManager]

    def post(self, request, workspace_slug):
        workspace = Workspace.objects.get(slug=workspace_slug)
        serializer = CreateDeveloperSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        if WorkspaceMembership.objects.filter(workspace=workspace, username=data["username"]).exists():
            return Response({"error": "Username taken in this workspace."}, status=400)

        password = data.get("password") or "".join(
            secrets.choice(string.ascii_letters + string.digits) for _ in range(12)
        )
        user = User.objects.create_user(
            email=data["email"], full_name=data["full_name"], password=password
        )
        membership = WorkspaceMembership.objects.create(
            user=user, workspace=workspace,
            username=data["username"], role=WorkspaceMembership.ROLE_DEVELOPER,
        )
        return Response({
            "membership": MembershipSerializer(membership).data,
            "generated_password": password,
            "login_url": f"/workspace/{workspace_slug}/login/",
        }, status=201)
