from rest_framework import serializers
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
        fields = ["id", "email", "full_name", "avatar_url", "created_at"]


class MembershipSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    avatar_url = serializers.CharField(source="user.avatar_url", read_only=True)

    class Meta:
        model = WorkspaceMembership
        fields = ["id", "user", "role", "username", "avatar_url", "is_active", "joined_at"]


class UpdateProfileSerializer(serializers.Serializer):
    full_name = serializers.CharField(required=False)
    email = serializers.EmailField(required=False)
    username = serializers.CharField(max_length=50, required=False)

    def validate_email(self, value):
        user = self.context["request"].user
        if User.objects.filter(email=value).exclude(pk=user.pk).exists():
            raise serializers.ValidationError("Email already in use.")
        return value


class CreateDeveloperSerializer(serializers.Serializer):
    full_name = serializers.CharField()
    email = serializers.EmailField()
    username = serializers.CharField(max_length=50)
    password = serializers.CharField(min_length=8, required=False)

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already registered.")
        return value
