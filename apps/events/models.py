from django.conf import settings
from django.db import models
from django.db.models import Q


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Event(models.Model):

    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        PUBLISHED = "published", "Published"
        CANCELLED = "cancelled", "Cancelled"

    organizer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="organized_events"
    )

    category = models.ForeignKey(
        Category,
          on_delete=models.PROTECT,
        related_name="events"
    )

    title = models.CharField(max_length=200)
    description = models.TextField()

    venue_name = models.CharField(max_length=200)
    location = models.CharField(max_length=255)

    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class TicketType(models.Model):
    event = models.ForeignKey(
        Event,
        related_name="ticket_types",
        on_delete=models.CASCADE,
    )
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=Q(price__gte=0),
                name="ticket_type_price_non_negative",
            ),
            models.CheckConstraint(
                check=Q(quantity__gt=0),
                name="ticket_type_quantity_positive",
            ),
        ]

    def __str__(self):
        return f"{self.name} ({self.event.title})"
