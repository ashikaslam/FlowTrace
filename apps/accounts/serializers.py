from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import User, WorkspaceMembership


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ["email", "full_name", "password"]

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "full_name", "created_at"]


class WorkspaceTokenSerializer(TokenObtainPairSerializer):
    """Login with workspace slug + username + password."""
    workspace_slug = serializers.CharField()
    username = serializers.CharField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Remove default email field, we use username + workspace
        self.fields.pop("email", None)

    def validate(self, attrs):
        from apps.workspaces.models import Workspace
        slug = attrs.get("workspace_slug")
        username = attrs.get("username")
        password = attrs.get("password")

        try:
            workspace = Workspace.objects.get(slug=slug)
            membership = WorkspaceMembership.objects.select_related("user").get(
                workspace=workspace, username=username, is_active=True
            )
        except Exception:
            raise serializers.ValidationError("Invalid workspace, username, or password.")

        user = membership.user
        if not user.check_password(password):
            raise serializers.ValidationError("Invalid credentials.")

        from rest_framework_simplejwt.tokens import RefreshToken
        refresh = RefreshToken.for_user(user)
        refresh["workspace_id"] = workspace.id
        refresh["workspace_slug"] = workspace.slug
        refresh["role"] = membership.role
        refresh["username"] = membership.username

        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "user": UserSerializer(user).data,
            "workspace": workspace.slug,
            "role": membership.role,
        }


class MembershipSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = WorkspaceMembership
        fields = ["id", "user", "role", "username", "is_active", "joined_at"]


class CreateDeveloperSerializer(serializers.Serializer):
    full_name = serializers.CharField()
    email = serializers.EmailField()
    username = serializers.CharField(max_length=50)
    password = serializers.CharField(min_length=8, required=False)

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already registered.")
        return value
