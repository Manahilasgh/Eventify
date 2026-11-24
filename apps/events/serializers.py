
from rest_framework import serializers
from django.db.models import Sum

from .models import Event, Category, TicketType


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "description"]


class TicketTypeSerializer(serializers.ModelSerializer):
    available_quantity = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = TicketType
        fields = [
            "id",
            "event",
            "name",
            "price",
            "quantity",
            "available_quantity",
            "created_at",
        ]
        read_only_fields = ["id", "event", "available_quantity", "created_at"]

    def get_available_quantity(self, obj):
        if hasattr(obj, "_available_quantity"):
            return obj._available_quantity
        booked = (
            obj.bookings.filter(status=obj.bookings.model.Status.CONFIRMED)
            .aggregate(total=Sum("quantity"))["total"]
            or 0
        )
        return obj.quantity - booked

    def validate_price(self, value):
        if value < 0:
            raise serializers.ValidationError("Price cannot be negative.")
        return value

    def validate_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError("Quantity must be greater than zero.")
        return value


class EventSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(
        source="category.name",
        read_only=True
    )

    organizer_email = serializers.EmailField(
        source="organizer.email",
        read_only=True
    )

    ticket_types = TicketTypeSerializer(
        many=True,
        read_only=True
    )

    class Meta:
        model = Event
        fields = [
            "id",
            "title",
            "description",
            "organizer",
            "category",
            "category_name",
            "organizer_email",
            "venue_name",
            "location",
            "start_datetime",
            "end_datetime",
            "status",
            "ticket_types",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "organizer",
            "status",
            "created_at",
        ]

    def validate(self, attrs):
        start = attrs.get(
            "start_datetime",
            getattr(self.instance, "start_datetime", None)
        )
        end = attrs.get(
            "end_datetime",
            getattr(self.instance, "end_datetime", None)
        )

        if start and end and end <= start:
            raise serializers.ValidationError(
                "Event end time must be after start time."
            )

        return attrs
