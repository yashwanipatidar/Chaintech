from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsOrganizerOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        # Allow read-only methods for anyone with view permissions, otherwise only organizer can modify
        if request.method in SAFE_METHODS:
            return True
        return hasattr(obj, 'organizer') and obj.organizer == request.user


class IsInvitedOrPublic(BasePermission):
    def has_object_permission(self, request, view, obj):
        # If the event is public, allow. Otherwise, allow if user is invited or is organizer.
        if getattr(obj, 'is_public', False):
            return True
        user = request.user
        # invited_users is a related manager — check membership safely
        organizer = getattr(obj, 'organizer', None)
        if user == organizer:
            return True
        try:
            return obj.invited_users.filter(pk=user.pk).exists()
        except Exception:
            return False
