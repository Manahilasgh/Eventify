from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.db import transaction

from .models import OrganizerProfile, User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    model = User

    list_display = (
        "id",
        "email",
        "first_name",
        "last_name",
        "role",
        "is_staff",
        "is_active",
    )

    ordering = ("email",)
    search_fields = ("email", "first_name", "last_name")

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Personal info", {"fields": ("first_name", "last_name", "role")}),
        ("Permissions", {
            "fields": (
                "is_active",
                "is_staff",
                "is_superuser",
                "groups",
                "user_permissions",
            )
        }),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "usable_password",
                    "password1",
                    "password2",
                    "role",
                ),
            },
        ),
    )


@admin.register(OrganizerProfile)
class OrganizerProfileAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "organization_name",
        "approval_status",
        "created_at",
    )
    list_filter = ("approval_status",)
    search_fields = ("organization_name", "user__email")
    readonly_fields = ("created_at",)
    ordering = ("-created_at",)

    def save_model(self, request, obj, form, change):
        """Keep User.role in sync with OrganizerProfile.approval_status."""
        with transaction.atomic():
            old_status = None
            if change:
                original = OrganizerProfile.objects.only(
                    "approval_status", "user_id"
                ).get(pk=obj.pk)
                old_status = original.approval_status

            new_status = obj.approval_status
            user = obj.user

            if not change and new_status == self.model.ApprovalStatus.APPROVED:
                user.role = user.Role.ORGANIZER
            elif change and old_status != new_status:
                if new_status == self.model.ApprovalStatus.APPROVED:
                    user.role = user.Role.ORGANIZER
                elif old_status == self.model.ApprovalStatus.APPROVED:
                    # Approval revoked or rejected: demote back to customer.
                    user.role = user.Role.CUSTOMER
            if change or new_status == self.model.ApprovalStatus.APPROVED:
                user.save()

            super().save_model(request, obj, form, change)
