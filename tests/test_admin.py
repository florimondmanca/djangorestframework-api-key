from unittest import mock

import pytest
from django.contrib import messages as dj_messages
from django.contrib.admin import site
from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from django.contrib.messages.middleware import MessageMiddleware
from django.contrib.sessions.middleware import SessionMiddleware
from django.http.request import HttpRequest
from django.test import RequestFactory
from test_project.heroes.admin import HeroAPIKeyModelAdmin
from test_project.heroes.models import Hero, HeroAPIKey

from rest_framework_api_key.admin import APIKeyModelAdmin
from rest_framework_api_key.models import APIKey


def build_admin_request(rf: RequestFactory, data: dict = None) -> HttpRequest:
    request = rf.post("/", data)

    # NOTE: all middleware must be instantiated before
    # any middleware can process the request.
    sessions = SessionMiddleware()
    messages = MessageMiddleware()

    sessions.process_request(request)
    messages.process_request(request)

    request.user = get_user_model().objects.get_or_create(username="test_user")[0]

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


@pytest.mark.django_db
def test_admin_revoke_single_api_key(rf: RequestFactory) -> None:
    request = build_admin_request(rf)

    admin = APIKeyModelAdmin(APIKey, site)
    api_key = APIKey.objects.create_key(name="test_admin_revoke_api_key")[0]
    queryset = APIKey.objects.filter(pk=api_key.pk)

    assert not api_key.revoked
    admin.revoke(request, queryset=queryset)
    api_key.refresh_from_db()
    messages = list(get_messages(request))
    assert len(messages) == 1
    assert messages[0].level == dj_messages.SUCCESS
    assert api_key.revoked


@pytest.mark.django_db
def test_admin_revoke_multiple_api_key(rf: RequestFactory) -> None:
    request = build_admin_request(rf)

    admin = APIKeyModelAdmin(APIKey, site)
    APIKey.objects.create_key(name="test_admin_revoke_api_key_1")
    APIKey.objects.create_key(name="test_admin_revoke_api_key_2")
    queryset = APIKey.objects.all()

    assert queryset.count() > 1
    admin.revoke(request, queryset=queryset)
    messages = list(get_messages(request))
    assert len(messages) == 1
    assert messages[0].level == dj_messages.ERROR


@pytest.mark.django_db
def test_admin_verify_api_key(rf: RequestFactory, ) -> None:
    admin = APIKeyModelAdmin(APIKey, site)
    api_key_1_obj, api_key_1_key = APIKey.objects.create_key(name="test_admin_verify_api_key_1")
    api_key_2_obj, api_key_2_key = APIKey.objects.create_key(name="test_admin_verify_api_key_2")

    assert api_key_1_obj.is_valid(api_key_1_key)
    assert api_key_2_obj.is_valid(api_key_2_key)

    # Test Form Load
    with mock.patch("rest_framework_api_key.admin.render") as mock_render:
        queryset = APIKey.objects.filter(pk=api_key_1_obj.pk)
        request = build_admin_request(rf)
        admin.verify(request, queryset=queryset)
        mock_render.assert_called_once()

    # Test Submit Invalid Form
    with mock.patch("rest_framework_api_key.admin.render") as mock_render:
        queryset = APIKey.objects.filter(pk=api_key_1_obj.pk)
        request = build_admin_request(rf, {"action": ["verify"], "apply": ["Verify"]})  # missing Key field
        admin.verify(request, queryset=queryset)
        messages = list(get_messages(request))
        mock_render.assert_called_once()
        assert len(messages) == 0

    # Test Submit Form with Wrong Key
    with mock.patch("rest_framework_api_key.admin.render") as mock_render:
        queryset = APIKey.objects.filter(pk=api_key_1_obj.pk)
        request = build_admin_request(rf, {"action": ["verify"], "apply": ["Verify"], "key": [api_key_2_key]})
        admin.verify(request, queryset=queryset)
        assert mock_render.call_count == 1
        messages = list(get_messages(request))
        assert len(messages) == 1
        assert messages[0].level == dj_messages.ERROR

        queryset = APIKey.objects.filter(pk=api_key_2_obj.pk)
        request = build_admin_request(rf, {"action": ["verify"], "apply": ["Verify"], "key": [api_key_1_key]})
        admin.verify(request, queryset=queryset)
        assert mock_render.call_count == 2
        messages = list(get_messages(request))
        assert len(messages) == 1
        assert messages[0].level == dj_messages.ERROR

        queryset = APIKey.objects.filter(pk=api_key_2_obj.pk)
        request = build_admin_request(rf, {"action": ["verify"], "apply": ["Verify"], "key": ["XXXXXXXXXXXXXXXXXX"]})
        admin.verify(request, queryset=queryset)
        assert mock_render.call_count == 3
        messages = list(get_messages(request))
        assert len(messages) == 1
        assert messages[0].level == dj_messages.ERROR

    # Test Submit Form with Correct Key
    with mock.patch("rest_framework_api_key.admin.render") as mock_render:
        queryset = APIKey.objects.filter(pk=api_key_1_obj.pk)
        request = build_admin_request(rf, {"action": ["verify"], "apply": ["Verify"], "key": [api_key_1_key]})
        admin.verify(request, queryset=queryset)
        assert mock_render.call_count == 1
        messages = list(get_messages(request))
        assert len(messages) == 1
        assert messages[0].level == dj_messages.SUCCESS

        queryset = APIKey.objects.filter(pk=api_key_2_obj.pk)
        request = build_admin_request(rf, {"action": ["verify"], "apply": ["Verify"], "key": [api_key_2_key]})
        admin.verify(request, queryset=queryset)
        assert mock_render.call_count == 2
        messages = list(get_messages(request))
        assert len(messages) == 1
        assert messages[0].level == dj_messages.SUCCESS


@pytest.mark.django_db
def test_admin_verify_multiple_api_key(rf: RequestFactory) -> None:
    request = build_admin_request(rf)

    admin = APIKeyModelAdmin(APIKey, site)
    APIKey.objects.create_key(name="test_admin_verify_api_key_1")
    APIKey.objects.create_key(name="test_admin_verify_api_key_2")
    queryset = APIKey.objects.all()

    assert queryset.count() > 1
    admin.verify(request, queryset=queryset)
    messages = list(get_messages(request))
    assert len(messages) == 1
    assert messages[0].level == dj_messages.ERROR
