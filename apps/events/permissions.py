from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsEventOrganizerOrReadOnly(BasePermission):
    message = "You can only modify events you organize."

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True

        return (
            request.user.is_authenticated
            and obj.organizer_id == request.user.id
        )
