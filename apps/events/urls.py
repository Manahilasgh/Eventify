from django.urls import path

from .views import (
    EventDetailAPIView,
    EventListCreateAPIView,
    EventPublishAPIView,
    MyEventsAPIView,
    TicketTypeDetailAPIView,
    TicketTypeListCreateAPIView,
    CategoryListAPIView
)

urlpatterns = [
    path("my-events/", MyEventsAPIView.as_view(), name="event-my-events"),
    path("<int:pk>/publish/", EventPublishAPIView.as_view(), name="event-publish"),
    path(
        "<int:event_id>/tickets/",
        TicketTypeListCreateAPIView.as_view(),
        name="ticket-type-list-create",
    ),
    path(
        "<int:event_id>/tickets/<int:ticket_id>/",
        TicketTypeDetailAPIView.as_view(),
        name="ticket-type-detail",
    ),
    path("", EventListCreateAPIView.as_view(), name="event-list-create"),
    path("<int:pk>/", EventDetailAPIView.as_view(), name="event-detail"),
    path(
    "categories/",
    CategoryListAPIView.as_view(),
    name="category-list",
),
]
