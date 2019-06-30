import typing

import pytest
from django.conf import settings
from django.http import HttpRequest
from django.test import override_settings

from .compat import nullcontext


def pytest_configure():
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
                "tests.project.heroes",
                "tests.project.events",
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
            ROOT_URLCONF="tests.project.project.urls",
            DATABASES={
                "default": {
                    "ENGINE": "django.db.backends.sqlite3",
                    "NAME": ":memory:",
                }
            },
        )
    )


@pytest.fixture
def view_with_permissions():
    from rest_framework.response import Response
    from rest_framework.views import APIView

    def create_view(*classes, **attrs):
        class View(APIView):
            permission_classes = classes

            def get(self, _):
                return Response()

        for name, value in attrs.items():
            setattr(View, name, value)

        return View.as_view()

    return create_view


def _create_user():
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
def fixture_key_header_config(request) -> dict:
    config = request.param

    if config.get("set_custom_header_setting"):
        ctx = override_settings(API_KEY_CUSTOM_HEADER=config["header"])
    else:
        ctx = nullcontext()

    with ctx:
        yield config


@pytest.fixture(name="build_create_request")
def fixture_build_create_request(key_header_config: dict):
    from rest_framework.test import APIRequestFactory, force_authenticate
    from rest_framework_api_key.models import AbstractAPIKey

    def build_create_request(model: typing.Type[AbstractAPIKey]):
        request_factory = APIRequestFactory()

        _MISSING = object()

        def create_request(
            authenticated: bool = False,
            authorization: str = _MISSING,
            key: str = None,
            key_modifier: typing.Callable[[str], str] = lambda key: key,
            **kwargs
        ):
            headers = {}

            header = None
            header_format = key_header_config["default"]
            header_name = key_header_config["header"]

            if key is not None:
                header = header_format.format(key=key)
            elif authorization is None:
                header = None
            else:
                # Automatically create and attach an API key.
                if authorization is not _MISSING:
                    header_format = authorization
                kwargs.setdefault("name", "test")
                _, key = model.objects.create_key(**kwargs)
                header = header_format.format(key=key_modifier(key))

            if header is not None:
                headers[header_name] = header

            request = request_factory.get("/test/", **headers)

            if authenticated:
                user = _create_user()
                force_authenticate(request, user)

            return request

        return create_request

    return build_create_request


@pytest.fixture(name="create_request")
def fixture_create_request(build_create_request) -> HttpRequest:
    from rest_framework_api_key.models import APIKey

    return build_create_request(APIKey)
