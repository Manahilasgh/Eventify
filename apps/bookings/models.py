from django.conf import settings
from django.db import models
from django.db.models import Q


class Booking(models.Model):

    class Status(models.TextChoices):
        CONFIRMED = "confirmed", "Confirmed"
        CANCELLED = "cancelled", "Cancelled"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="bookings",
        on_delete=models.PROTECT,
    )
    ticket_type = models.ForeignKey(
        "events.TicketType",
        related_name="bookings",
        on_delete=models.PROTECT,
    )
    quantity = models.PositiveIntegerField()
    total_price = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.CONFIRMED,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=Q(quantity__gt=0),
                name="booking_quantity_positive",
            ),
            models.CheckConstraint(
                check=Q(total_price__gte=0),
                name="booking_total_price_non_negative",
            ),
        ]
        ordering = ["-created_at"]

    def __str__(self):
        return f"Booking #{self.id} - {self.user.email} - {self.ticket_type.name} x{self.quantity}"