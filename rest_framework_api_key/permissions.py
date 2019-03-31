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

        try:
            name, secret_key = key.split(":")
        except ValueError:
            return False

        try:
            api_key = APIKey.objects.get(name=name, revoked=False)
        except APIKey.DoesNotExist:  # pylint: disable=no-member
            return False

        granted = check_secret_key(secret_key, api_key.encoded)

        return granted


class HasAPIKeyOrIsAuthenticated(permissions.BasePermission):
    """Authorize if a valid API key is provided or request is authenticated."""

    def has_permission(self, request, view):
        perms = [HasAPIKey(), permissions.IsAuthenticated()]
        return any(perm.has_permission(request, view) for perm in perms)
