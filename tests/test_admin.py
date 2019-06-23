import pytest
from django.contrib.admin import site
from django.contrib.messages import get_messages
from django.contrib.messages.middleware import MessageMiddleware
from django.contrib.sessions.middleware import SessionMiddleware
from django.test import RequestFactory

from rest_framework_api_key.admin import APIKeyModelAdmin
from rest_framework_api_key.models import APIKey

from .heroes.admin import HeroAPIKeyModelAdmin
from .heroes.models import Hero, HeroAPIKey


@pytest.fixture(name="req")
def fixture_req(rf: RequestFactory):
    messages = MessageMiddleware()
    sessions = SessionMiddleware()
    request = rf.get("/")
    sessions.process_request(request)
    messages.process_request(request)
    return request


@pytest.mark.django_db
@pytest.mark.parametrize(
    "model, model_admin, build_api_key",
    [
        (APIKey, APIKeyModelAdmin, lambda m: m(name="test")),
        (
            HeroAPIKey,
            HeroAPIKeyModelAdmin,
            lambda m: m(name="test", hero=Hero.objects.create()),
        ),
    ],
)
def test_save_model(req, model, model_admin, build_api_key):
    admin = model_admin(model, site)
    api_key = build_api_key(model)

    assert not api_key.pk
    admin.save_model(req, api_key)
    assert api_key.pk

    messages = get_messages(req)
    assert len(messages) == 1
