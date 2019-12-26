import typing

from django.conf import settings
from django.http import HttpRequest
from rest_framework import permissions

from .models import AbstractAPIKey, APIKey

if typing.TYPE_CHECKING:
    from django.db import models


class KeyParser:
    def get(self, request: HttpRequest) -> typing.Optional[str]:
        custom_header = getattr(settings, "API_KEY_CUSTOM_HEADER", None)

        if custom_header is not None:
            return self.get_from_header(request, custom_header)

        return self.get_from_authorization(request)

    def get_from_authorization(self, request: HttpRequest) -> typing.Optional[str]:
        authorization = request.META.get("HTTP_AUTHORIZATION")

        if not authorization:
            return None

        try:
            _, key = authorization.split("Api-Key ")
        except ValueError:
            key = None

        return key

    def get_from_header(self, request: HttpRequest, name: str) -> typing.Optional[str]:
        return request.META.get(name) or None


class BaseHasAPIKey(permissions.BasePermission):
    model = None  # type: typing.Type[models.Model]
    key_parser = KeyParser()

    def get_key(self, request: HttpRequest) -> typing.Optional[str]:
        return self.key_parser.get(request)

    def has_permission(self, request: HttpRequest, view: typing.Any) -> bool:
        assert self.model is not None, (
            "%s must define `.model` with the API key model to use"
            % self.__class__.__name__
        )
        key = self.get_key(request)
        if not key:
            return False
        return self.model.objects.is_valid(key)

    def has_object_permission(
        self, request: HttpRequest, view: typing.Any, obj: AbstractAPIKey
    ) -> bool:
        return self.has_permission(request, view)


class HasAPIKey(BaseHasAPIKey):
    model = APIKey
