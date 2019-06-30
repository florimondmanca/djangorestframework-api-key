import typing

from django.conf import settings
from django.http import HttpRequest
from rest_framework import permissions

from .models import AbstractAPIKey, APIKey


class KeyParser:
    def get(self, request: HttpRequest) -> typing.Optional[str]:
        custom_header = getattr(settings, "API_KEY_CUSTOM_HEADER", None)

        if custom_header is not None:
            return self.get_from_header(request, custom_header)

        return self.get_from_authorization(request)

    def get_from_authorization(
        self, request: HttpRequest
    ) -> typing.Optional[str]:
        authorization = request.META.get("HTTP_AUTHORIZATION")

        if not authorization:
            return None

        try:
            _, key = authorization.split("Api-Key ")
        except ValueError:
            key = None

        return key

    def get_from_header(
        self, request: HttpRequest, name: str
    ) -> typing.Optional[str]:
        return request.META.get(name) or None


class BaseHasAPIKey(permissions.BasePermission):
    model = None
    key_parser = KeyParser()

    def get_key(self, request: HttpRequest) -> typing.Optional[str]:
        return self.key_parser.get(request)

    def check(self, view: typing.Any) -> None:
        assert self.model is not None, (
            "%s must define `.model` with the API key model to use"
            % self.__class__.__name__
        )

    def has_permission(self, request: HttpRequest, view: typing.Any) -> bool:
        self.check(view)
        key = self.get_key(request)
        if not key:
            return False
        return self.model.objects.is_valid(key)

    def has_object_permission(
        self, request: HttpRequest, view: typing.Any, obj: AbstractAPIKey
    ) -> bool:
        return self.has_permission(request, view)


class BaseHasAPIKeyWithScopes(BaseHasAPIKey):
    def check(self, view: typing.Any) -> None:
        super().check(view)
        assert hasattr(view, "required_scopes"), (
            "%s must define `.required_scopes`" % view.__class__.__name__
        )

    def has_permission(self, request: HttpRequest, view: typing.Any) -> bool:
        if not super().has_permission(request, view):
            return False

        key = self.get_key(request)
        api_key = self.model.objects.get_from_secret(
            key
        )  # type: AbstractAPIKey

        return set(view.required_scopes).issubset(api_key.get_scopes())

    def has_object_permission(
        self, request: HttpRequest, view, obj: typing.Any
    ) -> bool:
        return self.has_permission(request, view)


class HasAPIKey(BaseHasAPIKey):
    model = APIKey


class HasAPIKeyWithScopes(BaseHasAPIKeyWithScopes):
    model = APIKey
