from rest_framework.permissions import BasePermission

from .models import OrganizerProfile


class IsApprovedOrganizer(BasePermission):
    """
    Allows access only to authenticated users whose role is 'organizer'
    and who have an OrganizerProfile with approval_status 'approved'.
    """

    message = (
        "Only approved organizers can perform this action. "
        "Submit an organizer application and wait for admin approval."
    )

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        if user.role != user.Role.ORGANIZER:
            return False
        return OrganizerProfile.objects.filter(
            user=user,
            approval_status=OrganizerProfile.ApprovalStatus.APPROVED,
        ).exists()