"""API key permissions."""

from rest_framework import permissions

from .models import APIKey
from .crypto import check


class HasAPIKey(permissions.BasePermission):
    """Authorize if a valid API key is provided.

    The request is authorized if, and only if:

    1. The `Authorization` header is present and correctly formatted:
    
    ```
    Authorization: Api-Key: $NAME:$VALUE
    ```

    2. An API key for this name exists and it has not been revoked.
    3. The given API key value matches the encoded version stored in database.
    """

    def has_permission(self, request, view) -> bool:
        authorization = request.META.get("HTTP_AUTHORIZATION")

        if authorization is None:
            return False

        _, _, key = authorization.partition("Api-Key: ")

        try:
            name, secret_key = key.split(":")
        except ValueError:
            return False

        try:
            api_key = APIKey.objects.get(name=name, revoked=False)
        except APIKey.DoesNotExist:  # pylint: disable=no-member
            return False

        granted = check(secret_key, api_key.encoded)

        return granted


class HasAPIKeyOrIsAuthenticated(permissions.BasePermission):
    """Authorize if a valid API key is provided or request is authenticated."""

    def has_permission(self, request, view):
        perms = [HasAPIKey(), permissions.IsAuthenticated()]
        return any(perm.has_permission(request, view) for perm in perms)
