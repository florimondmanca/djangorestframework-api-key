import pytest
from django.contrib.admin import site
from django.contrib.messages import get_messages
from django.contrib.messages.middleware import MessageMiddleware
from django.contrib.sessions.middleware import SessionMiddleware
from django.test import RequestFactory

from rest_framework_api_key.admin import APIKeyAdmin
from rest_framework_api_key.models import APIKey


@pytest.fixture(name="req")
def fixture_req(rf: RequestFactory):
    messages = MessageMiddleware()
    sessions = SessionMiddleware()
    request = rf.get("/")
    sessions.process_request(request)
    messages.process_request(request)
    return request


@pytest.mark.django_db
def test_save_model(req):
    admin = APIKeyAdmin(APIKey, site)
    api_key = APIKey(name="test")

    assert not api_key.pk
    admin.save_model(req, api_key)
    assert api_key.pk

    messages = get_messages(req)
    assert len(messages) == 1
