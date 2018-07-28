"""API key permissions."""

from rest_framework import permissions

from .models import APIKey
from .settings import API_KEY_HEADER


class HasAPIKey(permissions.BasePermission):
    """Authorize if a valid API key is provided.

    If the provided API key has been revoked, the request is not authorized.
    """

    def has_permission(self, request, view):
        api_key = request.META.get(API_KEY_HEADER, '')
        if not api_key:
            return False
        return APIKey.objects.filter(key=api_key, revoked=False).exists()


class HasAPIKeyOrIsAuthenticated(permissions.BasePermission):
    """Authorize if a valid API key is provided or request is authenticated."""

    def has_permission(self, request, view):
        perms = [
            HasAPIKey(),
            permissions.IsAuthenticated(),
        ]
        return any(perm.has_permission(request, view) for perm in perms)
