from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from .models import OrganizerProfile, User
from .admin import OrganizerProfileAdmin
from apps.events.models import Category, Event

User = get_user_model()


class UserRoleTests(TestCase):
    """Tests for the role field on the custom User model."""

    def test_new_user_defaults_to_customer(self):
        user = User.objects.create_user(
            email="buyer@example.com", password="StrongPass123"
        )
        self.assertEqual(user.role, User.Role.CUSTOMER)

    def test_registration_does_not_expose_role(self):
        self.client = APIClient()
        payload = {
            "email": "newbie@example.com",
            "password": "StrongPass123",
            "first_name": "New",
            "last_name": "User",
            "role": User.Role.ORGANIZER,  # must be ignored by public registration
        }
        response = self.client.post(reverse("register"), payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = User.objects.get(email="newbie@example.com")
        self.assertEqual(user.role, User.Role.CUSTOMER)

    def test_existing_login_and_current_user_endpoints_still_work(self):
        user = User.objects.create_user(
            email="me@example.com", password="StrongPass123"
        )
        self.client = APIClient()
        login_response = self.client.post(
            reverse("login"),
            {"email": "me@example.com", "password": "StrongPass123"},
            format="json",
        )
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)
        self.assertIn("access", login_response.data)

        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + login_response.data["access"]
        )
        me_response = self.client.get(reverse("current-user"))
        self.assertEqual(me_response.status_code, status.HTTP_200_OK)
        self.assertEqual(me_response.data["email"], "me@example.com")


class OrganizerApplicationTests(TestCase):
    """Tests for the organizer application endpoint."""

    def setUp(self):
        self.client = APIClient()
        self.customer = User.objects.create_user(
            email="customer@example.com", password="StrongPass123"
        )
        self.apply_url = reverse("apply-organizer")
        self.payload = {
            "organization_name": "Acme Events Ltd.",
            "description": "We organize great events.",
        }

    def test_customer_can_submit_organizer_application(self):
        self.client.force_authenticate(user=self.customer)
        response = self.client.post(self.apply_url, self.payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["organization_name"], "Acme Events Ltd.")
        self.assertTrue(
            OrganizerProfile.objects.filter(user=self.customer).exists()
        )

    def test_organizer_application_defaults_to_pending(self):
        self.client.force_authenticate(user=self.customer)
        self.client.post(self.apply_url, self.payload, format="json")
        profile = OrganizerProfile.objects.get(user=self.customer)
        self.assertEqual(
            profile.approval_status, OrganizerProfile.ApprovalStatus.PENDING
        )

    def test_application_does_not_escalate_role(self):
        """Applying must not self-approve or escalate the role via the API."""
        self.client.force_authenticate(user=self.customer)
        self.client.post(self.apply_url, self.payload, format="json")
        self.customer.refresh_from_db()
        self.assertEqual(self.customer.role, User.Role.CUSTOMER)

    def test_duplicate_application_is_rejected(self):
        self.client.force_authenticate(user=self.customer)
        first = self.client.post(self.apply_url, self.payload, format="json")
        self.assertEqual(first.status_code, status.HTTP_201_CREATED)

        second = self.client.post(self.apply_url, self.payload, format="json")
        self.assertEqual(second.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("organization_name", second.data)
        self.assertEqual(
            OrganizerProfile.objects.filter(user=self.customer).count(), 1
        )

    def test_unauthenticated_user_cannot_apply(self):
        response = self.client.post(self.apply_url, self.payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AdminOrganizerApprovalTests(TestCase):
    """Tests for the admin approval workflow in Django Admin."""

    def setUp(self):
        from django.contrib.admin.sites import AdminSite

        self.site = AdminSite()
        self.admin = OrganizerProfileAdmin(OrganizerProfile, self.site)
        self.admin_user = User.objects.create_superuser(
            email="admin@example.com", password="adminpass123"
        )

    def _make_request(self):
        from types import SimpleNamespace

        return SimpleNamespace(user=self.admin_user)

    def test_organizer_profile_registered_in_admin(self):
        from django.contrib.admin import site

        self.assertIn(OrganizerProfile, site._registry)

    def test_admin_approval_changes_user_role_to_organizer(self):
        user = User.objects.create_user(
            email="org@example.com", password="StrongPass123"
        )
        profile = OrganizerProfile.objects.create(
            user=user,
            organization_name="Acme Events Ltd.",
            approval_status=OrganizerProfile.ApprovalStatus.PENDING,
        )
        profile.approval_status = OrganizerProfile.ApprovalStatus.APPROVED
        form = type("Form", (), {"changed_data": ["approval_status"]})()
        self.admin.save_model(self._make_request(), profile, form, change=True)
        user.refresh_from_db()
        self.assertEqual(user.role, User.Role.ORGANIZER)

    def test_admin_rejection_changes_user_role_back_to_customer(self):
        user = User.objects.create_user(
            email="org2@example.com", password="StrongPass123",
            role=User.Role.ORGANIZER,
        )
        profile = OrganizerProfile.objects.create(
            user=user,
            organization_name="Acme Events Ltd.",
            approval_status=OrganizerProfile.ApprovalStatus.APPROVED,
        )
        profile.approval_status = OrganizerProfile.ApprovalStatus.REJECTED
        form = type("Form", (), {"changed_data": ["approval_status"]})()
        self.admin.save_model(self._make_request(), profile, form, change=True)
        user.refresh_from_db()
        self.assertEqual(user.role, User.Role.CUSTOMER)

    def test_admin_revocation_to_pending_changes_user_role_back_to_customer(self):
        user = User.objects.create_user(
            email="org3@example.com", password="StrongPass123",
            role=User.Role.ORGANIZER,
        )
        profile = OrganizerProfile.objects.create(
            user=user,
            organization_name="Acme Events Ltd.",
            approval_status=OrganizerProfile.ApprovalStatus.APPROVED,
        )
        profile.approval_status = OrganizerProfile.ApprovalStatus.PENDING
        form = type("Form", (), {"changed_data": ["approval_status"]})()
        self.admin.save_model(self._make_request(), profile, form, change=True)
        user.refresh_from_db()
        self.assertEqual(user.role, User.Role.CUSTOMER)

    def test_creating_new_profile_approved_in_admin_sets_role_to_organizer(self):
        user = User.objects.create_user(
            email="org4@example.com", password="StrongPass123"
        )
        profile = OrganizerProfile(
            user=user,
            organization_name="New Org",
            approval_status=OrganizerProfile.ApprovalStatus.APPROVED,
        )
        form = type("Form", (), {"changed_data": []})()
        self.admin.save_model(self._make_request(), profile, form, change=False)
        user.refresh_from_db()
        self.assertEqual(user.role, User.Role.ORGANIZER)
