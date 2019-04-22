import typing

from django.conf import settings
from rest_framework import permissions

from .models import APIKey


class HasAPIKey(permissions.BasePermission):
    def has_permission(self, request, view) -> bool:
        key = _get_key(request)

        if not key:
            return False

        return APIKey.objects.is_valid(key)

    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view)


def _get_key(request) -> typing.Optional[str]:
    custom_header = getattr(settings, "API_KEY_CUSTOM_HEADER", None)

    if custom_header is not None:
        return _get_key_from_custom_header(request, custom_header)

    return _get_key_from_authorization(request)


def _get_key_from_authorization(request) -> typing.Optional[str]:
    authorization = request.META.get("HTTP_AUTHORIZATION")

    if not authorization:
        return None

    try:
        _, key = authorization.split("Api-Key ")
    except ValueError:
        key = None

    return key


def _get_key_from_custom_header(request, name: str) -> typing.Optional[str]:
    header = request.META.get(name)
    return header if header else None
