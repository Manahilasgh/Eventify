from django.contrib import admin
from .models import Booking


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "ticket_type",
        "quantity",
        "total_price",
        "status",
        "created_at",
    )
    list_filter = ("status", "created_at")
    search_fields = (
        "user__email",
        "ticket_type__name",
        "ticket_type__event__title",
    )
    list_select_related = ("user", "ticket_type__event")
    ordering = ("-created_at",)
    readonly_fields = ("created_at",)