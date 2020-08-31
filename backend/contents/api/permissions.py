
from rest_framework import permissions


class IsAllowedUserLevel(permissions.IsAuthenticated):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        if not request.user.is_authenticated:
            return True
        result = super().has_permission(request, view)
        return result and request.user.level not in ('associate', )
