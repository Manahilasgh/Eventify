from rest_framework import serializers

from .models import Booking


class BookingCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating a booking. Only accepts ticket_type and quantity."""

    class Meta:
        model = Booking
        fields = ["ticket_type", "quantity"]

    def validate_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError("Quantity must be greater than zero.")
        return value


class BookingSerializer(serializers.ModelSerializer):
    """Read serializer for booking responses."""

    event_id = serializers.IntegerField(source="ticket_type.event.id", read_only=True)
    event_title = serializers.CharField(source="ticket_type.event.title", read_only=True)
    ticket_type_name = serializers.CharField(source="ticket_type.name", read_only=True)

    class Meta:
        model = Booking
        fields = [
            "id",
            "event_id",
            "event_title",
            "ticket_type",
            "ticket_type_name",
            "quantity",
            "total_price",
            "status",
            "created_at",
        ]
        read_only_fields = fields