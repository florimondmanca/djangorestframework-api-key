import base64
import binascii
import typing

from django.conf import settings
from django.http import HttpRequest
from rest_framework import permissions

from .models import AbstractAPIKey, APIKey


class KeyParser:
    keyword = "Api-Key"

    def get(self, request: HttpRequest) -> typing.Optional[str]:
        custom_header = getattr(settings, "API_KEY_CUSTOM_HEADER", None)

        if custom_header is not None:
            api_key = self.get_from_header(request, custom_header)
        else:
            api_key = self.get_from_authorization(request)

        base64_encoded = getattr(settings, "API_KEY_BASE64_ENCODED", False)
        if base64_encoded and api_key:
            try:
                api_key = base64.b64decode(api_key, validate=True).decode("UTF-8")
            except (
                binascii.Error,
                UnicodeDecodeError,
            ):  # API-Key not correctly base64 encoded.
                api_key = None
        return api_key

    def get_from_authorization(self, request: HttpRequest) -> typing.Optional[str]:
        authorization = request.META.get("HTTP_AUTHORIZATION")

        if not authorization:
            return None

        try:
            _, key = authorization.split("{} ".format(self.keyword))
        except ValueError:
            key = None

        return key

    def get_from_header(self, request: HttpRequest, name: str) -> typing.Optional[str]:
        return request.META.get(name) or None


class BaseHasAPIKey(permissions.BasePermission):
    model: typing.Optional[typing.Type[AbstractAPIKey]] = None
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
