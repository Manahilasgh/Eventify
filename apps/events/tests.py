from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from django.contrib.auth import get_user_model
from apps.accounts.models import OrganizerProfile
from .models import Category, Event, TicketType

User = get_user_model()


class EventAccessTests(TestCase):
    """Tests for role-based access to event endpoints."""

    def setUp(self):
        self.client = APIClient()
        self.category = Category.objects.create(
            name="Music", description="Live music events"
        )

        self.customer = User.objects.create_user(
            email="buyer@example.com", password="StrongPass123"
        )

        self.pending_organizer = User.objects.create_user(
            email="pending@example.com", password="StrongPass123"
        )
        OrganizerProfile.objects.create(
            user=self.pending_organizer,
            organization_name="Pending Org",
            approval_status=OrganizerProfile.ApprovalStatus.PENDING,
        )

        self.approved_organizer = User.objects.create_user(
            email="approved@example.com", password="StrongPass123",
            role=User.Role.ORGANIZER,
        )
        OrganizerProfile.objects.create(
            user=self.approved_organizer,
            organization_name="Approved Org",
            approval_status=OrganizerProfile.ApprovalStatus.APPROVED,
        )

        self.other_organizer = User.objects.create_user(
            email="other@example.com", password="StrongPass123",
            role=User.Role.ORGANIZER,
        )
        OrganizerProfile.objects.create(
            user=self.other_organizer,
            organization_name="Other Org",
            approval_status=OrganizerProfile.ApprovalStatus.APPROVED,
        )

        self.event_payload = {
            "title": "Live Concert",
            "description": "A great live music event",
            "category": self.category.id,
            "venue_name": "Main Hall",
            "location": "City Center",
            "start_datetime": "2027-06-01T19:00:00Z",
            "end_datetime": "2027-06-01T22:00:00Z",
        }

    def test_pending_organizer_cannot_create_events(self):
        self.client.force_authenticate(user=self.pending_organizer)
        response = self.client.post(
            reverse("event-list-create"), self.event_payload, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_authenticated_customer_cannot_create_events(self):
        self.client.force_authenticate(user=self.customer)
        response = self.client.post(
            reverse("event-list-create"), self.event_payload, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_approved_organizer_can_create_events(self):
        self.client.force_authenticate(user=self.approved_organizer)
        response = self.client.post(
            reverse("event-list-create"), self.event_payload, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Event.objects.count(), 1)

    def test_created_event_is_assigned_to_authenticated_organizer(self):
        self.client.force_authenticate(user=self.approved_organizer)
        self.client.post(
            reverse("event-list-create"), self.event_payload, format="json"
        )
        event = Event.objects.first()
        self.assertEqual(event.organizer, self.approved_organizer)
        self.assertEqual(event.status, Event.Status.DRAFT)

    def test_organizer_cannot_update_another_organizers_event(self):
        self.client.force_authenticate(user=self.approved_organizer)
        create_response = self.client.post(
            reverse("event-list-create"), self.event_payload, format="json"
        )
        event_id = create_response.data["id"]

        self.client.force_authenticate(user=self.other_organizer)
        response = self.client.patch(
            reverse("event-detail", args=[event_id]),
            {"title": "Hijacked Title"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_organizer_cannot_delete_another_organizers_event(self):
        self.client.force_authenticate(user=self.approved_organizer)
        create_response = self.client.post(
            reverse("event-list-create"), self.event_payload, format="json"
        )
        event_id = create_response.data["id"]

        self.client.force_authenticate(user=self.other_organizer)
        response = self.client.delete(
            reverse("event-detail", args=[event_id])
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Event.objects.filter(id=event_id).exists())

    def test_approved_organizer_can_update_own_event(self):
        self.client.force_authenticate(user=self.approved_organizer)
        create_response = self.client.post(
            reverse("event-list-create"), self.event_payload, format="json"
        )
        event_id = create_response.data["id"]

        response = self.client.patch(
            reverse("event-detail", args=[event_id]),
            {"title": "Updated Concert Title"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "Updated Concert Title")

    def _list_response(self):
        response = self.client.get(reverse("event-list-create"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        return response.data

    def test_public_can_view_published_events(self):
        self.client.force_authenticate(user=self.approved_organizer)
        self.client.post(
            reverse("event-list-create"), self.event_payload, format="json"
        )
        published = Event.objects.first()
        published.status = Event.Status.PUBLISHED
        published.save()

        self.client.force_authenticate(user=None)
        data = self._list_response()
        results = data["results"] if isinstance(data, dict) else data
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["id"], published.id)

    def test_draft_events_are_hidden_from_public_get(self):
        self.client.force_authenticate(user=self.approved_organizer)
        self.client.post(
            reverse("event-list-create"), self.event_payload, format="json"
        )
        self.client.force_authenticate(user=None)
        data = self._list_response()
        results = data["results"] if isinstance(data, dict) else data
        self.assertEqual(len(results), 0)


class MyEventsAPITests(TestCase):
    """Tests for the organizer's own events endpoint."""

    def setUp(self):
        self.client = APIClient()
        self.category = Category.objects.create(
            name="Music", description="Live music events"
        )

        self.customer = User.objects.create_user(
            email="buyer@example.com", password="StrongPass123"
        )

        self.pending_organizer = User.objects.create_user(
            email="pending@example.com", password="StrongPass123"
        )
        OrganizerProfile.objects.create(
            user=self.pending_organizer,
            organization_name="Pending Org",
            approval_status=OrganizerProfile.ApprovalStatus.PENDING,
        )

        self.approved_organizer = User.objects.create_user(
            email="approved@example.com", password="StrongPass123",
            role=User.Role.ORGANIZER,
        )
        OrganizerProfile.objects.create(
            user=self.approved_organizer,
            organization_name="Approved Org",
            approval_status=OrganizerProfile.ApprovalStatus.APPROVED,
        )

        self.other_organizer = User.objects.create_user(
            email="other@example.com", password="StrongPass123",
            role=User.Role.ORGANIZER,
        )
        OrganizerProfile.objects.create(
            user=self.other_organizer,
            organization_name="Other Org",
            approval_status=OrganizerProfile.ApprovalStatus.APPROVED,
        )

        self.my_events_url = reverse("event-my-events")

    def _create_event(self, user, status=Event.Status.DRAFT, title="Event"):
        return Event.objects.create(
            organizer=user,
            category=self.category,
            title=title,
            description="A description",
            venue_name="Main Hall",
            location="City Center",
            status=status,
            start_datetime="2027-06-01T19:00:00Z",
            end_datetime="2027-06-01T22:00:00Z",
        )

    def test_approved_organizer_can_list_own_draft_events(self):
        self.client.force_authenticate(user=self.approved_organizer)
        self._create_event(self.approved_organizer, Event.Status.DRAFT)
        self._create_event(self.approved_organizer, Event.Status.PUBLISHED)
        response = self.client.get(self.my_events_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data
        results = data["results"] if isinstance(data, dict) else data
        self.assertEqual(len(results), 2)

    def test_organizer_cannot_see_another_organizers_events(self):
        self.client.force_authenticate(user=self.approved_organizer)
        self._create_event(self.other_organizer, Event.Status.DRAFT, title="Other")
        response = self.client.get(self.my_events_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data
        results = data["results"] if isinstance(data, dict) else data
        self.assertEqual(len(results), 0)

    def test_customer_cannot_access_my_events(self):
        self.client.force_authenticate(user=self.customer)
        response = self.client.get(self.my_events_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_pending_organizer_cannot_access_my_events(self):
        self.client.force_authenticate(user=self.pending_organizer)
        response = self.client.get(self.my_events_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_my_events_rejected(self):
        self.client.force_authenticate(user=None)
        response = self.client.get(self.my_events_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class EventPublishAPITests(TestCase):
    """Tests for the event publishing endpoint."""

    def setUp(self):
        self.client = APIClient()
        self.category = Category.objects.create(
            name="Music", description="Live music events"
        )

        self.customer = User.objects.create_user(
            email="buyer@example.com", password="StrongPass123"
        )

        self.approved_organizer = User.objects.create_user(
            email="approved@example.com", password="StrongPass123",
            role=User.Role.ORGANIZER,
        )
        OrganizerProfile.objects.create(
            user=self.approved_organizer,
            organization_name="Approved Org",
            approval_status=OrganizerProfile.ApprovalStatus.APPROVED,
        )

        self.other_organizer = User.objects.create_user(
            email="other@example.com", password="StrongPass123",
            role=User.Role.ORGANIZER,
        )
        OrganizerProfile.objects.create(
            user=self.other_organizer,
            organization_name="Other Org",
            approval_status=OrganizerProfile.ApprovalStatus.APPROVED,
        )

        self.draft_event = Event.objects.create(
            organizer=self.approved_organizer,
            category=self.category,
            title="Live Concert",
            description="A great live music event",
            venue_name="Main Hall",
            location="City Center",
            status=Event.Status.DRAFT,
            start_datetime="2027-06-01T19:00:00Z",
            end_datetime="2027-06-01T22:00:00Z",
        )
        self.publish_url = reverse("event-publish", kwargs={"pk": self.draft_event.id})

    def _publish(self, user, pk=None):
        self.client.force_authenticate(user=user)
        return self.client.post(
            reverse("event-publish", kwargs={"pk": pk or self.draft_event.id})
        )

    def test_approved_organizer_can_publish_valid_draft_event(self):
        response = self._publish(self.approved_organizer)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.draft_event.refresh_from_db()
        self.assertEqual(self.draft_event.status, Event.Status.PUBLISHED)
        self.assertEqual(response.data["status"], "published")

    def test_published_event_appears_in_public_list(self):
        self._publish(self.approved_organizer)
        self.client.force_authenticate(user=None)
        response = self.client.get(reverse("event-list-create"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data
        results = data["results"] if isinstance(data, dict) else data
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["id"], self.draft_event.id)

    def test_draft_event_does_not_appear_in_public_list(self):
        self.client.force_authenticate(user=None)
        response = self.client.get(reverse("event-list-create"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data
        results = data["results"] if isinstance(data, dict) else data
        self.assertEqual(len(results), 0)

    def test_organizer_cannot_publish_someone_elses_event(self):
        response = self._publish(self.other_organizer)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.draft_event.refresh_from_db()
        self.assertEqual(self.draft_event.status, Event.Status.DRAFT)

    def test_customer_cannot_publish_event(self):
        response = self._publish(self.customer)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_publishing_already_published_event_returns_400(self):
        self.draft_event.status = Event.Status.PUBLISHED
        self.draft_event.save()
        response = self._publish(self.approved_organizer)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("status", response.data)

    def test_publishing_cancelled_event_returns_400(self):
        self.draft_event.status = Event.Status.CANCELLED
        self.draft_event.save()
        response = self._publish(self.approved_organizer)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("status", response.data)

    def test_publishing_past_start_date_returns_400(self):
        self.draft_event.start_datetime = "2020-01-01T19:00:00Z"
        self.draft_event.end_datetime = "2020-01-01T22:00:00Z"
        self.draft_event.save()
        response = self._publish(self.approved_organizer)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("start_datetime", response.data)

    def test_publishing_end_before_start_returns_400(self):
        self.draft_event.start_datetime = "2027-06-01T22:00:00Z"
        self.draft_event.end_datetime = "2027-06-01T19:00:00Z"
        self.draft_event.save()
        response = self._publish(self.approved_organizer)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("end_datetime", response.data)

    def test_publishing_blank_required_fields_returns_400(self):
        self.draft_event.title = "   "
        self.draft_event.description = "   "
        self.draft_event.venue_name = ""
        self.draft_event.location = ""
        self.draft_event.save()
        response = self._publish(self.approved_organizer)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        for field in ("title", "description", "venue_name", "location"):
            self.assertIn(field, response.data)

    def test_ordinary_patch_cannot_modify_status(self):
        self.client.force_authenticate(user=self.approved_organizer)
        response = self.client.patch(
            reverse("event-detail", kwargs={"pk": self.draft_event.id}),
            {"status": Event.Status.PUBLISHED},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.draft_event.refresh_from_db()
        self.assertEqual(self.draft_event.status, Event.Status.DRAFT)


class TicketTypeAPITests(TestCase):
    """Tests for ticket type CRUD and access control."""

    def setUp(self):
        self.client = APIClient()
        self.category = Category.objects.create(
            name="Music", description="Live music events"
        )

        self.customer = User.objects.create_user(
            email="buyer@example.com", password="StrongPass123"
        )

        self.pending_organizer = User.objects.create_user(
            email="pending@example.com", password="StrongPass123"
        )
        OrganizerProfile.objects.create(
            user=self.pending_organizer,
            organization_name="Pending Org",
            approval_status=OrganizerProfile.ApprovalStatus.PENDING,
        )

        self.approved_organizer = User.objects.create_user(
            email="approved@example.com", password="StrongPass123",
            role=User.Role.ORGANIZER,
        )
        OrganizerProfile.objects.create(
            user=self.approved_organizer,
            organization_name="Approved Org",
            approval_status=OrganizerProfile.ApprovalStatus.APPROVED,
        )

        self.other_organizer = User.objects.create_user(
            email="other@example.com", password="StrongPass123",
            role=User.Role.ORGANIZER,
        )
        OrganizerProfile.objects.create(
            user=self.other_organizer,
            organization_name="Other Org",
            approval_status=OrganizerProfile.ApprovalStatus.APPROVED,
        )

        self.published_event = Event.objects.create(
            organizer=self.approved_organizer,
            category=self.category,
            title="Published Concert",
            description="A published event",
            venue_name="Main Hall",
            location="City Center",
            status=Event.Status.PUBLISHED,
            start_datetime="2027-06-01T19:00:00Z",
            end_datetime="2027-06-01T22:00:00Z",
        )

        self.draft_event = Event.objects.create(
            organizer=self.approved_organizer,
            category=self.category,
            title="Draft Concert",
            description="A draft event",
            venue_name="Main Hall",
            location="City Center",
            status=Event.Status.DRAFT,
            start_datetime="2027-07-01T19:00:00Z",
            end_datetime="2027-07-01T22:00:00Z",
        )

        self.other_event = Event.objects.create(
            organizer=self.other_organizer,
            category=self.category,
            title="Other Organizer Event",
            description="Someone else's event",
            venue_name="Other Hall",
            location="Other City",
            status=Event.Status.PUBLISHED,
            start_datetime="2027-08-01T19:00:00Z",
            end_datetime="2027-08-01T22:00:00Z",
        )

        self.ticket_payload = {
            "name": "Regular",
            "price": "1000.00",
            "quantity": 100,
        }

    def _ticket_list_url(self, event_id):
        return reverse("ticket-type-list-create", kwargs={"event_id": event_id})

    def _ticket_detail_url(self, event_id, ticket_id):
        return reverse(
            "ticket-type-detail",
            kwargs={"event_id": event_id, "ticket_id": ticket_id},
        )

    def test_approved_organizer_creates_ticket_type_for_own_event(self):
        self.client.force_authenticate(user=self.approved_organizer)
        response = self.client.post(
            self._ticket_list_url(self.draft_event.id),
            self.ticket_payload,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["name"], "Regular")
        self.assertEqual(response.data["price"], "1000.00")
        self.assertEqual(response.data["quantity"], 100)
        self.assertEqual(response.data["event"], self.draft_event.id)

    def test_customer_cannot_create_ticket_type(self):
        self.client.force_authenticate(user=self.customer)
        response = self.client.post(
            self._ticket_list_url(self.draft_event.id),
            self.ticket_payload,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_pending_organizer_cannot_create_ticket_type(self):
        self.client.force_authenticate(user=self.pending_organizer)
        response = self.client.post(
            self._ticket_list_url(self.draft_event.id),
            self.ticket_payload,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_organizer_cannot_create_ticket_type_for_others_event(self):
        self.client.force_authenticate(user=self.approved_organizer)
        response = self.client.post(
            self._ticket_list_url(self.other_event.id),
            self.ticket_payload,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_organizer_can_update_own_ticket_type(self):
        self.client.force_authenticate(user=self.approved_organizer)
        create_response = self.client.post(
            self._ticket_list_url(self.draft_event.id),
            self.ticket_payload,
            format="json",
        )
        ticket_id = create_response.data["id"]

        response = self.client.patch(
            self._ticket_detail_url(self.draft_event.id, ticket_id),
            {"name": "VIP", "price": "2500.00", "quantity": 30},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "VIP")
        self.assertEqual(response.data["price"], "2500.00")
        self.assertEqual(response.data["quantity"], 30)

    def test_organizer_can_delete_own_ticket_type(self):
        self.client.force_authenticate(user=self.approved_organizer)
        create_response = self.client.post(
            self._ticket_list_url(self.draft_event.id),
            self.ticket_payload,
            format="json",
        )
        ticket_id = create_response.data["id"]

        response = self.client.delete(
            self._ticket_detail_url(self.draft_event.id, ticket_id)
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(
            TicketType.objects.filter(id=ticket_id).exists()
        )

    def test_negative_price_is_rejected(self):
        self.client.force_authenticate(user=self.approved_organizer)
        payload = dict(self.ticket_payload, price="-10.00")
        response = self.client.post(
            self._ticket_list_url(self.draft_event.id),
            payload,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("price", response.data)

    def test_zero_quantity_is_rejected(self):
        self.client.force_authenticate(user=self.approved_organizer)
        payload = dict(self.ticket_payload, quantity=0)
        response = self.client.post(
            self._ticket_list_url(self.draft_event.id),
            payload,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("quantity", response.data)

    def test_published_event_ticket_types_are_publicly_accessible(self):
        self.client.force_authenticate(user=self.approved_organizer)
        self.client.post(
            self._ticket_list_url(self.published_event.id),
            self.ticket_payload,
            format="json",
        )

        self.client.force_authenticate(user=None)
        response = self.client.get(
            self._ticket_list_url(self.published_event.id)
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data
        results = data["results"] if isinstance(data, dict) else data
        self.assertEqual(len(results), 1)

    def test_draft_event_ticket_types_hidden_from_public(self):
        self.client.force_authenticate(user=self.approved_organizer)
        self.client.post(
            self._ticket_list_url(self.draft_event.id),
            self.ticket_payload,
            format="json",
        )

        self.client.force_authenticate(user=None)
        response = self.client.get(
            self._ticket_list_url(self.draft_event.id)
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_approved_organizer_can_view_own_draft_event_ticket_types(self):
        self.client.force_authenticate(user=self.approved_organizer)
        self.client.post(
            self._ticket_list_url(self.draft_event.id),
            self.ticket_payload,
            format="json",
        )

        response = self.client.get(
            self._ticket_list_url(self.draft_event.id)
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data
        results = data["results"] if isinstance(data, dict) else data
        self.assertEqual(len(results), 1)

    def test_ticket_types_appear_in_event_detail_response(self):
        self.client.force_authenticate(user=self.approved_organizer)
        self.client.post(
            self._ticket_list_url(self.published_event.id),
            self.ticket_payload,
            format="json",
        )

        self.client.force_authenticate(user=None)
        response = self.client.get(
            reverse("event-detail", kwargs={"pk": self.published_event.id})
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("ticket_types", response.data)
        self.assertEqual(len(response.data["ticket_types"]), 1)
        self.assertEqual(response.data["ticket_types"][0]["name"], "Regular")
