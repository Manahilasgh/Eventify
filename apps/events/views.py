from django.db import transaction
from django.http import Http404
from django.utils import timezone
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from django.db.models import Q
from django.db.models import Sum
from django.db.models.deletion import ProtectedError
from rest_framework.exceptions import ValidationError

from .models import Event, TicketType, Category
from .permissions import IsEventOrganizerOrReadOnly
from .serializers import EventSerializer, TicketTypeSerializer, CategorySerializer
from apps.accounts.permissions import IsApprovedOrganizer
from apps.accounts.models import OrganizerProfile


class EventListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = EventSerializer

    def get_permissions(self):
        if self.request.method == "POST":
            return [
                permissions.IsAuthenticated(),
                IsApprovedOrganizer(),
            ]
        return [permissions.AllowAny()]

    def get_queryset(self):
        return (
            Event.objects
            .filter(status=Event.Status.PUBLISHED)
            .select_related("category", "organizer")
            .prefetch_related("ticket_types")
            .order_by("start_datetime")
        )

    def perform_create(self, serializer):
        serializer.save(organizer=self.request.user)


class EventDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = EventSerializer

    def get_permissions(self):
        if self.request.method in permissions.SAFE_METHODS:
            return [permissions.AllowAny()]

        return [
            permissions.IsAuthenticated(),
            IsApprovedOrganizer(),
            IsEventOrganizerOrReadOnly(),
        ]

    def get_queryset(self):
        queryset = Event.objects.select_related(
            "category",
            "organizer"
        ).prefetch_related("ticket_types")

        user = self.request.user

        if self.request.method in permissions.SAFE_METHODS:
            if (
                user.is_authenticated
                and user.role == user.Role.ORGANIZER
                and OrganizerProfile.objects.filter(
                    user=user,
                    approval_status=OrganizerProfile.ApprovalStatus.APPROVED,
                ).exists()
            ):
                return queryset.filter(
                    Q(status=Event.Status.PUBLISHED)
                    | Q(organizer=user)
                )

            return queryset.filter(
                status=Event.Status.PUBLISHED
            )

        return queryset.filter(organizer=user)

    def perform_destroy(self, instance):
        try:
            instance.delete()
        except ProtectedError:
            raise ValidationError({
                "detail": "Cannot delete an event with existing booking records."
            })


class MyEventsAPIView(generics.ListAPIView):
    """
    List the authenticated organizer's own events (draft, published,
    and cancelled). Other organizers' events never appear.
    """

    serializer_class = EventSerializer
    permission_classes = [
        permissions.IsAuthenticated,
        IsApprovedOrganizer,
    ]

    def get_queryset(self):
        return (
            Event.objects
            .filter(organizer=self.request.user)
            .select_related("category", "organizer")
            .prefetch_related("ticket_types")
            .order_by("-created_at")
        )


class EventPublishAPIView(APIView):
    """
    Publish a draft event owned by the authenticated organizer.

    POST /api/events/<int:pk>/publish/
    """

    permission_classes = [
        permissions.IsAuthenticated,
        IsApprovedOrganizer,
    ]

    def post(self, request, pk):
        with transaction.atomic():
            # Row-level lock for safe concurrent publish attempts.
            try:
                event = Event.objects.select_for_update().get(pk=pk)
            except Event.DoesNotExist:
                return Response(
                    {"detail": "Not found."},
                    status=status.HTTP_404_NOT_FOUND,
                )

            # Ownership enforced before any status change.
            if event.organizer_id != request.user.id:
                return Response(
                    {"detail": "Not found."},
                    status=status.HTTP_404_NOT_FOUND,
                )

            # Only draft events can be published.
            if event.status != Event.Status.DRAFT:
                if event.status == Event.Status.PUBLISHED:
                    return Response(
                        {"status": ["This event is already published."]},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                return Response(
                    {
                        "status": [
                            "Only draft events can be published. "
                            "Cancelled events cannot be published."
                        ]
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            errors = {}

            title = (event.title or "").strip()
            if not title:
                errors["title"] = ["Title cannot be empty or whitespace."]

            description = (event.description or "").strip()
            if not description:
                errors["description"] = [
                    "Description cannot be empty or whitespace."
                ]

            if not (event.venue_name or "").strip():
                errors["venue_name"] = ["Venue name is required."]

            if not (event.location or "").strip():
                errors["location"] = ["Location is required."]

            if not event.category_id:
                errors["category"] = ["Category is required."]

            now = timezone.now()
            if event.start_datetime and event.start_datetime <= now:
                errors["start_datetime"] = [
                    "Start date/time must be in the future."
                ]

            if (
                event.start_datetime
                and event.end_datetime
                and event.end_datetime <= event.start_datetime
            ):
                errors["end_datetime"] = [
                    "End date/time must be after start date/time."
                ]

            if errors:
                return Response(errors, status=status.HTTP_400_BAD_REQUEST)

            event.status = Event.Status.PUBLISHED
            event.save()

            serializer = EventSerializer(event, context={"request": request})
            return Response(serializer.data, status=status.HTTP_200_OK)


class TicketTypeListCreateAPIView(generics.ListCreateAPIView):
    """
    List ticket types for an event (GET) or create a new ticket type (POST).

    GET /api/events/{event_id}/tickets/
    POST /api/events/{event_id}/tickets/
    """

    serializer_class = TicketTypeSerializer

    def get_permissions(self):
        if self.request.method == "POST":
            return [
                permissions.IsAuthenticated(),
                IsApprovedOrganizer(),
            ]
        return [permissions.AllowAny()]

    def _get_accessible_event(self, event_id):
        """Return the event if accessible to the current user, else raise 404."""
        try:
            event = Event.objects.only("id", "status", "organizer_id").get(
                pk=event_id
            )
        except Event.DoesNotExist:
            raise Http404

        # Published events are publicly accessible.
        if event.status == Event.Status.PUBLISHED:
            return event

        user = self.request.user
        # Draft/cancelled events: only the owning approved organizer.
        if (
            user.is_authenticated
            and user.role == user.Role.ORGANIZER
            and event.organizer_id == user.id
            and OrganizerProfile.objects.filter(
                user=user,
                approval_status=OrganizerProfile.ApprovalStatus.APPROVED,
            ).exists()
        ):
            return event

        raise Http404

    def get_queryset(self):
        event_id = self.kwargs["event_id"]
        self._get_accessible_event(event_id)
        return (
            TicketType.objects
            .filter(event_id=event_id)
            .select_related("event")
        )

    def perform_create(self, serializer):
        event_id = self.kwargs["event_id"]
        event = self._get_accessible_event(event_id)
        # Published events are publicly readable, but only the owner may create
        # ticket types. _get_accessible_event already enforces ownership for
        # draft events; enforce it explicitly here for published events.
        if event.organizer_id != self.request.user.id:
            raise Http404
        serializer.save(event=event)


class TicketTypeDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    Update (PATCH) or delete (DELETE) a ticket type.

    PATCH /api/events/{event_id}/tickets/{ticket_id}/
    DELETE /api/events/{event_id}/tickets/{ticket_id}/
    """

    serializer_class = TicketTypeSerializer
    permission_classes = [
        permissions.IsAuthenticated,
        IsApprovedOrganizer,
    ]

    @transaction.atomic
    def perform_update(self, serializer):
        ticket = TicketType.objects.select_for_update().get(
            pk=serializer.instance.pk
        )

        booked = ticket.bookings.filter(
            status=ticket.bookings.model.Status.CONFIRMED
        ).aggregate(total=Sum("quantity"))["total"] or 0

        quantity = serializer.validated_data.get(
            "quantity", ticket.quantity
        )

        if quantity < booked:
            raise ValidationError({
                "quantity": f"Quantity cannot be less than {booked} booked tickets."
            })

        serializer.instance = ticket
        serializer.save()

    def get_queryset(self):
        event_id = self.kwargs["event_id"]
        return TicketType.objects.filter(
            id=self.kwargs["ticket_id"],
            event_id=event_id,
            event__organizer_id=self.request.user.id,
        ).select_related("event")

    def get_object(self):
        queryset = self.get_queryset()
        try:
            obj = queryset.get()
        except TicketType.DoesNotExist:
            raise Http404
        return obj

    def perform_destroy(self, instance):
        try:
            instance.delete()
        except ProtectedError:
            raise ValidationError({
                "detail": "Cannot delete a ticket type with existing booking records."
            })

class CategoryListAPIView(generics.ListAPIView):
    queryset = Category.objects.all().order_by("name")
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]