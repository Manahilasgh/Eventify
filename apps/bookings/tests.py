from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from django.contrib.auth import get_user_model
from apps.accounts.models import OrganizerProfile
from apps.events.models import Category, Event, TicketType
from .models import Booking

User = get_user_model()

HTTP_401_UNAUTHORIZED = 401
HTTP_403_FORBIDDEN = 403
HTTP_201_CREATED = 201
HTTP_400_BAD_REQUEST = 400


class BookingAPITests(TestCase):
    """Core booking creation tests."""

    def setUp(self):
        self.client = APIClient()
        self.category = Category.objects.create(name="Music")
        self.customer = User.objects.create_user(
            email="buyer@example.com", password="StrongPass123")
        self.approved_organizer = User.objects.create_user(
            email="approved@example.com", password="StrongPass123",
            role=User.Role.ORGANIZER)
        OrganizerProfile.objects.create(user=self.approved_organizer,
                                        organization_name="Org",
                                        approval_status="approved")
        self.published_event = Event.objects.create(
            organizer=self.approved_organizer, category=self.category,
            title="Published Concert", description="",
            venue_name="Main Hall", location="City Center",
            status="published", start_datetime="2027-06-01T19:00:00Z",
            end_datetime="2027-06-01T22:00:00Z")
        self.ticket_type = TicketType.objects.create(
            event=self.published_event, name="Regular", price="1000.00",
            quantity=100)
        self.booking_url = reverse("booking-create")

    def _authenticate(self, user):
        self.client.force_authenticate(user=user)

    def test_customer_can_book_available_tickets(self):
        self._authenticate(self.customer)
        response = self.client.post(
            self.booking_url,
            {"ticket_type": self.ticket_type.id, "quantity": 2},
            format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["quantity"], 2)
        self.assertEqual(response.data["status"], "confirmed")
        self.assertEqual(response.data["total_price"], "2000.00")

    def test_booking_created_with_confirmed_status(self):
        self._authenticate(self.customer)
        self.client.post(
            self.booking_url,
            {"ticket_type": self.ticket_type.id, "quantity": 2},
            format="json")
        booking = Booking.objects.first()
        self.assertEqual(booking.status, Booking.Status.CONFIRMED)

    def test_total_price_calculated_correctly(self):
        self._authenticate(self.customer)
        response = self.client.post(
            self.booking_url,
            {"ticket_type": self.ticket_type.id, "quantity": 3},
            format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["total_price"], "3000.00")

    def test_unauthenticated_booking_rejected(self):
        response = self.client.post(
            self.booking_url,
            {"ticket_type": self.ticket_type.id, "quantity": 2},
            format="json")
        self.assertEqual(response.status_code, HTTP_401_UNAUTHORIZED)

    def test_approved_organizer_cannot_book_as_customer(self):
        self._authenticate(self.approved_organizer)
        response = self.client.post(
            self.booking_url,
            {"ticket_type": self.ticket_type.id, "quantity": 2},
            format="json")
        self.assertEqual(response.status_code, HTTP_403_FORBIDDEN)

    def test_booking_quantity_zero_rejected(self):
        self._authenticate(self.customer)
        response = self.client.post(
            self.booking_url,
            {"ticket_type": self.ticket_type.id, "quantity": 0},
            format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_booking_beyond_capacity_rejected(self):
        self._authenticate(self.customer)
        response = self.client.post(
            self.booking_url,
            {"ticket_type": self.ticket_type.id, "quantity": 101},
            format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_draft_event_cannot_be_booked(self):
        draft_event = Event.objects.create(
            organizer=self.approved_organizer, category=self.category,
            title="Draft Concert", description="",
            venue_name="Main Hall", location="City Center",
            status="draft", start_datetime="2027-07-01T19:00:00Z",
            end_datetime="2027-07-01T22:00:00Z")
        ticket_type = TicketType.objects.create(
            event=draft_event, name="Draft Ticket", price="500.00", quantity=50)
        self._authenticate(self.customer)
        response = self.client.post(
            self.booking_url,
            {"ticket_type": ticket_type.id, "quantity": 2},
            format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_cancelled_event_cannot_be_booked(self):
        cancelled_event = Event.objects.create(
            organizer=self.approved_organizer, category=self.category,
            title="Cancelled Concert", description="",
            venue_name="Main Hall", location="City Center",
            status="cancelled", start_datetime="2027-07-01T19:00:00Z",
            end_datetime="2027-07-01T22:00:00Z")
        ticket_type = TicketType.objects.create(
            event=cancelled_event, name="Cancelled Ticket", price="500.00", quantity=50)
        self._authenticate(self.customer)
        response = self.client.post(
            self.booking_url,
            {"ticket_type": ticket_type.id, "quantity": 2},
            format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_past_event_cannot_be_booked(self):
        past_event = Event.objects.create(
            organizer=self.approved_organizer, category=self.category,
            title="Past Concert", description="",
            venue_name="Main Hall", location="City Center",
            status="published", start_datetime="2020-01-01T19:00:00Z",
            end_datetime="2020-01-01T22:00:00Z")
        ticket_type = TicketType.objects.create(
            event=past_event, name="Past Ticket", price="500.00", quantity=50)
        self._authenticate(self.customer)
        response = self.client.post(
            self.booking_url,
            {"ticket_type": ticket_type.id, "quantity": 2},
            format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class AvailableQuantityTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.category = Category.objects.create(name="Music")
        self.customer = User.objects.create_user(
            email="buyer@example.com", password="StrongPass123")
        self.approved_organizer = User.objects.create_user(
            email="approved@example.com", password="StrongPass123",
            role=User.Role.ORGANIZER)
        OrganizerProfile.objects.create(user=self.approved_organizer,
                                        organization_name="Org",
                                        approval_status="approved")
        self.published_event = Event.objects.create(
            organizer=self.approved_organizer, category=self.category,
            title="Published Concert", description="",
            venue_name="Main Hall", location="City Center",
            status="published", start_datetime="2027-06-01T19:00:00Z",
            end_datetime="2027-06-01T22:00:00Z")
        self.ticket_type = TicketType.objects.create(
            event=self.published_event, name="Regular", price="1000.00",
            quantity=100)

    def test_confirmed_bookings_reduce_available_quantity(self):
        self.client.force_authenticate(user=self.customer)
        self.client.post(
            reverse("booking-create"),
            {"ticket_type": self.ticket_type.id, "quantity": 3},
            format="json")
        self.ticket_type.refresh_from_db()
        from apps.events.serializers import TicketTypeSerializer
        serializer = TicketTypeSerializer(self.ticket_type)
        self.assertEqual(serializer.data["available_quantity"], 97)

    def test_cancelled_bookings_do_not_reduce_available_quantity(self):
        self.client.force_authenticate(user=self.customer)
        Booking.objects.create(user=self.customer,
                              ticket_type=self.ticket_type,
                              quantity=5,
                              total_price=self.ticket_type.price * 5,
                              status=Booking.Status.CANCELLED)
        self.ticket_type.refresh_from_db()
        from apps.events.serializers import TicketTypeSerializer
        serializer = TicketTypeSerializer(self.ticket_type)
        self.assertEqual(serializer.data["available_quantity"], 100)

    def test_available_quantity_in_ticket_type_list_response(self):
        self.client.force_authenticate(user=self.customer)
        self.client.post(
            reverse("booking-create"),
            {"ticket_type": self.ticket_type.id, "quantity": 10},
            format="json")
        response = self.client.get(
            reverse("ticket-type-list-create", kwargs={"event_id": self.published_event.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data
        results = data["results"] if isinstance(data, dict) else data
        self.assertEqual(results[0]["available_quantity"], 90)


class MyBookingsTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.category = Category.objects.create(name="Music")
        self.customer = User.objects.create_user(
            email="buyer@example.com", password="StrongPass123")
        self.other_customer = User.objects.create_user(
            email="otherbuyer@example.com", password="StrongPass123")
        self.approved_organizer = User.objects.create_user(
            email="approved@example.com", password="StrongPass123",
            role=User.Role.ORGANIZER)
        OrganizerProfile.objects.create(user=self.approved_organizer,
                                        organization_name="Org",
                                        approval_status="approved")
        self.published_event = Event.objects.create(
            organizer=self.approved_organizer, category=self.category,
            title="Published Concert", description="",
            venue_name="Main Hall", location="City Center",
            status="published", start_datetime="2027-06-01T19:00:00Z",
            end_datetime="2027-06-01T22:00:00Z")
        self.ticket_type = TicketType.objects.create(
            event=self.published_event, name="Regular", price="1000.00",
            quantity=100)
        self.booking_url = reverse("booking-create")
        self.my_bookings_url = reverse("booking-my-bookings")

    def _authenticate(self, user):
        self.client.force_authenticate(user=user)

    def test_customer_sees_only_own_bookings(self):
        self._authenticate(self.customer)
        self.client.post(self.booking_url,
                         {"ticket_type": self.ticket_type.id, "quantity": 2},
                         format="json")
        self._authenticate(self.other_customer)
        self.client.post(self.booking_url,
                         {"ticket_type": self.ticket_type.id, "quantity": 1},
                         format="json")
        self._authenticate(self.customer)
        response = self.client.get(self.my_bookings_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data
        results = data["results"] if isinstance(data, dict) else data
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["quantity"], 2)

    def test_my_bookings_requires_authentication(self):
        self.client.force_authenticate(user=None)
        response = self.client.get(self.my_bookings_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_my_bookings_includes_confirmed_and_cancelled(self):
        self._authenticate(self.customer)
        self.client.post(self.booking_url,
                         {"ticket_type": self.ticket_type.id, "quantity": 2},
                         format="json")
        booking = Booking.objects.first()
        booking.status = Booking.Status.CANCELLED
        booking.save()
        response = self.client.get(self.my_bookings_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data
        results = data["results"] if isinstance(data, dict) else data
        self.assertEqual(len(results), 1)

    def test_my_bookings_ordered_newest_first(self):
        self._authenticate(self.customer)
        self.client.post(self.booking_url,
                         {"ticket_type": self.ticket_type.id, "quantity": 1},
                         format="json")
        self.client.post(self.booking_url,
                         {"ticket_type": self.ticket_type.id, "quantity": 2},
                         format="json")
        response = self.client.get(self.my_bookings_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data
        results = data["results"] if isinstance(data, dict) else data
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]["quantity"], 2)
        self.assertEqual(results[1]["quantity"], 1)
