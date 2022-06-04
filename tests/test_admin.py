import pytest
from django.contrib.admin import site
from django.contrib.messages import get_messages
from django.contrib.messages.middleware import MessageMiddleware
from django.contrib.sessions.middleware import SessionMiddleware
from django.http.request import HttpRequest
from django.http.response import HttpResponse
from django.test import RequestFactory
from test_project.heroes.admin import HeroAPIKeyModelAdmin
from test_project.heroes.models import Hero, HeroAPIKey

from rest_framework_api_key.admin import APIKeyModelAdmin
from rest_framework_api_key.models import APIKey


def build_admin_request(rf: RequestFactory) -> HttpRequest:
    request = rf.post("/")

    def get_response(request: HttpRequest) -> HttpResponse:
        raise NotImplementedError  # pragma: no cover  # Unused in these tests.

    # NOTE: all middleware must be instantiated before
    # any middleware can process the request.
    sessions = SessionMiddleware(get_response)
    messages = MessageMiddleware(sessions.get_response)

    sessions.process_request(request)
    messages.process_request(request)

    return request


@pytest.mark.django_db
def test_admin_readonly_fields(rf: RequestFactory) -> None:
    request = build_admin_request(rf)

    admin = APIKeyModelAdmin(APIKey, site)

    assert admin.get_readonly_fields(request) == ("prefix",)

    api_key = APIKey(name="test")
    assert admin.get_readonly_fields(request, obj=api_key) == ("prefix",)

    api_key = APIKey(name="test", revoked=True)
    assert admin.get_readonly_fields(request, obj=api_key) == (
        "prefix",
        "name",
        "revoked",
        "expiry_date",
    )


@pytest.mark.django_db
def test_admin_create_api_key(rf: RequestFactory) -> None:
    request = build_admin_request(rf)

    admin = APIKeyModelAdmin(APIKey, site)
    api_key = APIKey(name="test")

    assert not api_key.pk
    admin.save_model(request, obj=api_key)
    assert api_key.pk

    messages = get_messages(request)
    assert len(messages) == 1


@pytest.mark.django_db
def test_admin_create_custom_api_key(rf: RequestFactory) -> None:
    request = build_admin_request(rf)

    admin = HeroAPIKeyModelAdmin(HeroAPIKey, site)
    api_key = HeroAPIKey(name="test", hero=Hero.objects.create())

    assert not api_key.pk
    admin.save_model(request, obj=api_key)
    assert api_key.pk

    messages = get_messages(request)
    assert len(messages) == 1


@pytest.mark.django_db
def test_admin_update_api_key(rf: RequestFactory) -> None:
    request = build_admin_request(rf)

    admin = APIKeyModelAdmin(APIKey, site)
    api_key, _ = APIKey.objects.create_key(name="test")

    api_key.name = "another-test"
    admin.save_model(request, obj=api_key)
    refreshed = APIKey.objects.get(pk=api_key.pk)
    assert refreshed.name == "another-test"
