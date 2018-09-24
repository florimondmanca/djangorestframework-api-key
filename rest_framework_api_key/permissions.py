"""API key permissions."""

from rest_framework import permissions

from .models import APIKey
from .settings import API_TOKEN_HEADER, API_SECRET_KEY_HEADER
from .crypto import hash_token


class HasAPIKey(permissions.BasePermission):
    """Authorize if a valid API token and secret key are provided.

    The request is not authorized if:
    - The token or the secret key headers are missing
    - There is no API key for the given token
    - The token hased by the given secret key does not match the hash stored
    in database.

    In all other cases, the request is authorized.
    """

    def has_permission(self, request, view):
        """Check whether the API key grants access to a view."""
        token = request.META.get(API_TOKEN_HEADER, '')
        secret_key = request.META.get(API_SECRET_KEY_HEADER, '')

        # Token and secret key must have been given
        if not token or not secret_key:
            return False

        # An unrevoked API key for this token must exist
        api_key = APIKey.objects.filter(token=token, revoked=False).first()
        if api_key is None:
            return False

        # Compare the hash of the given token by the given secret_key
        # to the hash stored no the api_key.
        hashed_token = hash_token(token, secret_key)
        granted = hashed_token == api_key.hashed_token

        return granted


class HasAPIKeyOrIsAuthenticated(permissions.BasePermission):
    """Authorize if a valid API key is provided or request is authenticated."""

    def has_permission(self, request, view):
        perms = [
            HasAPIKey(),
            permissions.IsAuthenticated(),
        ]
        return any(perm.has_permission(request, view) for perm in perms)
