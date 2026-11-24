from django.db import IntegrityError, transaction
from rest_framework import generics, permissions, serializers

from .models import OrganizerProfile
from .serializers import (
    OrganizerApplicationSerializer,
    RegisterSerializer,
    UserSerializer,
)


class RegisterAPIView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]


class CurrentUserAPIView(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


class ApplyOrganizerAPIView(generics.CreateAPIView):
    serializer_class = OrganizerApplicationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        user = self.request.user
        if OrganizerProfile.objects.filter(user=user).exists():
            raise serializers.ValidationError(
                {
                    "organization_name": [
                        "You have already submitted an organizer application. "
                        "Duplicate applications are not allowed."
                    ]
                }
            )
        try:
            with transaction.atomic():
                serializer.save(user=user)
        except IntegrityError:
            raise serializers.ValidationError(
                {
                    "organization_name": [
                        "You have already submitted an organizer application. "
                        "Duplicate applications are not allowed."
                    ]
                }
            )
