from django.db import models, transaction
from django.utils import timezone
from rest_framework import generics, permissions, status, serializers
from rest_framework.response import Response

from apps.events.models import TicketType

from .models import Booking
from .serializers import BookingCreateSerializer, BookingSerializer


class IsCustomer(permissions.BasePermission):
    message = "Only customers can perform this action."
    def has_permission(self, request, view):
        u = request.user
        return bool(u and u.is_authenticated and u.role == u.Role.CUSTOMER)


class BookingCreateAPIView(generics.CreateAPIView):
    serializer_class = BookingCreateSerializer
    permission_classes = [permissions.IsAuthenticated, IsCustomer]

    def perform_create(self, serializer):
        ticket_type = serializer.validated_data["ticket_type"]
        quantity = serializer.validated_data["quantity"]
        user = self.request.user
        with transaction.atomic():
            tt = TicketType.objects.select_for_update().get(pk=ticket_type.pk)
            event = tt.event
            if event.status != event.Status.PUBLISHED:
                raise serializers.ValidationError("Bookings only for published events.")
            if event.start_datetime and event.start_datetime <= timezone.now():
                raise serializers.ValidationError("Event already started.")
            booked = Booking.objects.filter(ticket_type=tt, status=Booking.Status.CONFIRMED).aggregate(models.Sum("quantity"))["quantity__sum"] or 0
            remaining = tt.quantity - booked
            if quantity > remaining:
                raise serializers.ValidationError(f"Not enough tickets. {remaining} remaining.")
            total = tt.price * quantity
            serializer.save(user=user, ticket_type=tt, quantity=quantity, total_price=total, status=Booking.Status.CONFIRMED)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        instance = serializer.instance
        response_serializer = BookingSerializer(instance, context={"request": request})
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)


class MyBookingsAPIView(generics.ListAPIView):
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]
    def get_queryset(self):
        return Booking.objects.filter(user=self.request.user).select_related("ticket_type__event").order_by("-created_at")


class BookingDetailAPIView(generics.RetrieveAPIView):
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]
    def get_queryset(self):
        return Booking.objects.filter(user=self.request.user)


class BookingCancelAPIView(generics.UpdateAPIView):
    """
    PUT /api/bookings/{id}/cancel/
    Cancel a confirmed booking.
    """
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Booking.objects.all()

    def update(self, request, *args, **kwargs):
        booking = self.get_object()
        user = request.user

        # Only the booking owner can cancel
        if booking.user_id != user.id:
            return Response(
                {"detail": "You do not have permission to cancel this booking."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Only confirmed bookings can be cancelled
        if booking.status != Booking.Status.CONFIRMED:
            if booking.status == Booking.Status.CANCELLED:
                return Response(
                    {"detail": "This booking is already cancelled."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            return Response(
                {"detail": "Only confirmed bookings can be cancelled."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Check if event has already started
        event = booking.ticket_type.event
        if event.start_datetime and event.start_datetime <= timezone.now():
            return Response(
                {"detail": "Cannot cancel booking after the event has started."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        with transaction.atomic():
            # Lock the booking row first, then the ticket type
            booking_lock = Booking.objects.select_for_update().get(pk=booking.pk)
            ticket_type_lock = TicketType.objects.select_for_update().get(pk=booking.ticket_type_id)

            # Update booking status
            booking_lock.status = Booking.Status.CANCELLED
            booking_lock.save()

            # Availability is automatically restored because our availability
            # calculation excludes cancelled bookings (SUM of confirmed quantities only)

        # Return updated booking
        response_serializer = BookingSerializer(booking_lock, context={"request": request})
        return Response(response_serializer.data, status=status.HTTP_200_OK)
