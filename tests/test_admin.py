import pytest
from django.contrib.admin import site
from django.contrib.messages import get_messages
from django.contrib.messages.middleware import MessageMiddleware
from django.contrib.sessions.middleware import SessionMiddleware
from django.http.request import HttpRequest
from django.test import RequestFactory
from test_project.heroes.admin import HeroAPIKeyModelAdmin
from test_project.heroes.models import Hero, HeroAPIKey

from rest_framework_api_key.admin import APIKeyModelAdmin
from rest_framework_api_key.models import APIKey


def dummy_get_response(request):  # pragma: no cover
    return None


def build_admin_request(rf: RequestFactory) -> HttpRequest:
    request = rf.post("/")

    # NOTE: all middleware must be instantiated before
    # any middleware can process the request.
    sessions = SessionMiddleware(dummy_get_response)
    messages = MessageMiddleware(dummy_get_response)

    sessions.process_request(request)
    messages.process_request(request)

    return request


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
