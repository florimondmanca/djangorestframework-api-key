import pytest
from django.contrib.admin import ModelAdmin, site
from django.contrib.auth import login
from django.contrib.auth.middleware import AuthenticationMiddleware
from django.contrib.auth.models import User
from django.contrib.messages import get_messages
from django.contrib.messages.middleware import MessageMiddleware
from django.contrib.sessions.middleware import SessionMiddleware
from django.test import RequestFactory

from rest_framework_api_key.admin import APIKeyModelAdmin
from rest_framework_api_key.models import APIKey

from .project.heroes.admin import HeroAPIKeyModelAdmin
from .project.heroes.models import Hero, HeroAPIKey


@pytest.fixture(name="req")
def fixture_req(rf: RequestFactory):
    messages = MessageMiddleware()
    sessions = SessionMiddleware()
    request = rf.post("/")
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
def test_create(req, model, model_admin, build_api_key):
    admin = model_admin(model, site)  # type: ModelAdmin
    api_key = build_api_key(model)

    assert not api_key.pk
    admin.save_model(req, obj=api_key)
    assert api_key.pk

    messages = get_messages(req)
    assert len(messages) == 1
