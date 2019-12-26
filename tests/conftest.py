import typing

import pytest
from django.conf import settings
from django.contrib.auth.base_user import AbstractBaseUser
from django.http import HttpRequest
from django.test import override_settings

from .compat import nullcontext


def pytest_configure() -> None:
    settings.configure(
        **dict(
            SECRET_KEY="abcd",
            INSTALLED_APPS=[
                # Mandatory
                "django.contrib.contenttypes",
                # Permissions
                "django.contrib.auth",
                # Admin
                "django.contrib.admin",
                "django.contrib.messages",
                "django.contrib.sessions",
                # Project
                "rest_framework",
                "rest_framework_api_key",
                "test_project.heroes",
            ],
            TEMPLATES=[
                # Admin
                {
                    "BACKEND": "django.template.backends.django.DjangoTemplates",
                    "OPTIONS": {
                        "context_processors": [
                            "django.contrib.auth.context_processors.auth",
                            "django.contrib.messages.context_processors.messages",
                        ]
                    },
                }
            ],
            MIDDLEWARE=[
                # Admin
                "django.contrib.messages.middleware.MessageMiddleware",
                "django.contrib.sessions.middleware.SessionMiddleware",
                "django.contrib.auth.middleware.AuthenticationMiddleware",
            ],
            ROOT_URLCONF="test_project.project.urls",
            DATABASES={
                "default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}
            },
        )
    )


@pytest.fixture
def view_with_permissions() -> typing.Callable:
    from rest_framework.decorators import api_view, permission_classes
    from rest_framework.response import Response

    def create_view(*classes: type) -> typing.Callable:
        @api_view()
        @permission_classes(classes)
        def view(*args: typing.Any) -> Response:
            return Response()

        return view

    return create_view


def _create_user() -> AbstractBaseUser:
    from django.contrib.auth import get_user_model

    User = get_user_model()
    return User.objects.create_user(username="foo", password="bar")


@pytest.fixture(
    name="key_header_config",
    params=[
        {"header": "HTTP_AUTHORIZATION", "default": "Api-Key {key}"},
        {
            "header": "HTTP_X_API_KEY",
            "default": "{key}",
            "set_custom_header_setting": True,
        },
    ],
)
def fixture_key_header_config(request: typing.Any) -> typing.Iterator[dict]:
    config: dict = request.param

    ctx: typing.ContextManager[None]
    if config.get("set_custom_header_setting"):
        ctx = override_settings(API_KEY_CUSTOM_HEADER=config["header"])  # type: ignore
    else:
        ctx = nullcontext()

    with ctx:
        yield config


@pytest.fixture(name="build_create_request")
def fixture_build_create_request(key_header_config: dict) -> typing.Callable:
    from rest_framework.test import APIRequestFactory, force_authenticate
    from rest_framework_api_key.models import AbstractAPIKey

    def build_create_request(model: typing.Type[AbstractAPIKey]) -> typing.Callable:
        request_factory = APIRequestFactory()

        _MISSING = object()

        def create_request(
            authenticated: bool = False, **kwargs: typing.Any,
        ) -> HttpRequest:
            headers = {}

            authorization = kwargs.pop("authorization", _MISSING)

            if authorization is not None:
                kwargs.setdefault("name", "test")
                _, key = model.objects.create_key(**kwargs)

                if callable(authorization):
                    authorization = authorization(key)

                if authorization is _MISSING:
                    authorization = key_header_config["default"]

                headers[key_header_config["header"]] = authorization.format(key=key)

            request = request_factory.get("/test/", **headers)

            if authenticated:
                user = _create_user()
                force_authenticate(request, user)

            return request

        return create_request

    return build_create_request


@pytest.fixture(name="create_request")
def fixture_create_request(build_create_request: typing.Callable) -> typing.Callable:
    from rest_framework_api_key.models import APIKey

    return build_create_request(APIKey)
