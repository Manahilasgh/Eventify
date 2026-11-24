from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import OrganizerProfile

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        min_length=8,
        style={"input_type": "password"}
    )

    class Meta:
        model = User
        fields = ["id", "email", "password", "first_name", "last_name"]
        read_only_fields = ["id"]

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "first_name", "last_name", "role",]
        read_only_fields = fields


class OrganizerApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrganizerProfile
        fields = [
            "id",
            "organization_name",
            "description",
            "approval_status",
            "created_at",
        ]
        read_only_fields = ["id", "approval_status", "created_at"]
