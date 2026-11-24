
from django.contrib import admin
from .models import Category, Event, TicketType


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "description")
    search_fields = ("name",)


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "organizer",
        "category",
        "start_datetime",
        "status",
    )

    list_filter = ("status", "category", "start_datetime")

    search_fields = (
        "title",
        "description",
        "organizer__email",
    )

    list_select_related = ("organizer", "category")

    ordering = ("-created_at",)


@admin.register(TicketType)
class TicketTypeAdmin(admin.ModelAdmin):
    list_display = ("id", "event", "name", "price", "quantity")
    search_fields = ("name", "event__title")
    list_select_related = ("event",)
