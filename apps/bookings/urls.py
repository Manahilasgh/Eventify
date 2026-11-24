from django.urls import path

from .views import BookingCreateAPIView, BookingDetailAPIView, MyBookingsAPIView, BookingCancelAPIView

urlpatterns = [
    path("", BookingCreateAPIView.as_view(), name="booking-create"),
    path("my-bookings/", MyBookingsAPIView.as_view(), name="booking-my-bookings"),
    path("<int:pk>/", BookingDetailAPIView.as_view(), name="booking-detail"),
    path("<int:pk>/cancel/", BookingCancelAPIView.as_view(), name="booking-cancel"),
]
