"""API key permissions."""

from rest_framework import permissions

from .models import APIKey
from .helpers import check_secret_key


class HasAPIKey(permissions.BasePermission):
    """Authorize if a valid API key is provided."""

    def has_permission(self, request, view) -> bool:
        authorization = request.META.get(
            "Authorization", request.META.get("HTTP_AUTHORIZATION")
        )

        if authorization is None:
            return False

        _, _, key = authorization.partition("Api-Key ")

        usable_keys = APIKey.objects.filter(revoked=False)

        return any(
            check_secret_key(key, encoded)
            for encoded in usable_keys.values_list("encoded", flat=True)
        )


class HasAPIKeyOrIsAuthenticated(permissions.BasePermission):
    """Authorize if a valid API key is provided or request is authenticated."""

    def has_permission(self, request, view):
        perms = [HasAPIKey(), permissions.IsAuthenticated()]
        return any(perm.has_permission(request, view) for perm in perms)
