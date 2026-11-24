from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from .views import RegisterAPIView, CurrentUserAPIView, ApplyOrganizerAPIView

urlpatterns = [
    path("register/", RegisterAPIView.as_view(), name="register"),
    path("login/", TokenObtainPairView.as_view(), name="login"),
    path("refresh/", TokenRefreshView.as_view(), name="token-refresh"),
    path("apply-organizer/", ApplyOrganizerAPIView.as_view(), name="apply-organizer"),
    path("me/", CurrentUserAPIView.as_view(), name="current-user"),
]
