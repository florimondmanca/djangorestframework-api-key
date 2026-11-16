import typing

import packaging.version
from django.conf import settings
from django.http import HttpRequest
from rest_framework import __version__ as __drf_version__
from rest_framework import permissions

from .models import AbstractAPIKey, APIKey

_drf_version = packaging.version.parse(__drf_version__)
_3_14_0 = packaging.version.parse("3.14.0")


class KeyParser:
    keyword = "Api-Key"

    def get(self, request: HttpRequest) -> typing.Optional[str]:
        custom_header = getattr(settings, "API_KEY_CUSTOM_HEADER", None)

        if custom_header is not None:
            return self.get_from_header(request, custom_header)

        return self.get_from_authorization(request)

    def get_from_authorization(self, request: HttpRequest) -> typing.Optional[str]:
        authorization = request.META.get("HTTP_AUTHORIZATION", "")

        if not authorization:
            return None

        keyword, found, key = authorization.partition(" ")

        if not found:
            return None

        if keyword.lower() != self.keyword.lower():
            return None

        return key

    def get_from_header(self, request: HttpRequest, name: str) -> typing.Optional[str]:
        return request.META.get(name) or None


class BaseHasAPIKey(permissions.BasePermission):
    model: typing.Optional[typing.Type[AbstractAPIKey]] = None
    key_parser = KeyParser()

    def get_key(self, request: HttpRequest) -> typing.Optional[str]:
        return self.key_parser.get(request)

    def _is_key_valid(self, request: HttpRequest, key: str) -> bool:
        assert self.model is not None
        raw_request = getattr(request, "_request", request)

        cache = getattr(raw_request, "_api_key_validation_cache", None)
        if cache is None:
            cache = {}
            raw_request._api_key_validation_cache = cache

        cache_key = (self.model, key)
        if cache_key not in cache:
            cache[cache_key] = self.model.objects.is_valid(key)

        return cache[cache_key]

    def has_permission(self, request: HttpRequest, view: typing.Any) -> bool:
        assert self.model is not None, (
            "%s must define `.model` with the API key model to use"
            % self.__class__.__name__
        )
        key = self.get_key(request)
        if not key:
            return False
        return self._is_key_valid(request, key)

    def has_object_permission(
        self, request: HttpRequest, view: typing.Any, obj: AbstractAPIKey
    ) -> bool:
        if _drf_version < _3_14_0:  # pragma: no cover
            # Before DRF 3.14.0 (released in Sept 2022), bitwise OR would skip
            # .has_permision() and only call .has_object_permission(), resulting in
            # API key permissions not being checked unless we implemented
            # .has_object_permission().
            # Since 3.14.0, DRF appropriately checks for both .has_permission() and
            # .has_object_permission() when checking object permissions of a bitwise OR.
            # We kept the old redundant behavior to avoid regressions for users who have
            # not updated their DRF yet.
            return self.has_permission(request, view)

        return super().has_object_permission(request, view, obj)


class HasAPIKey(BaseHasAPIKey):
    model = APIKey
