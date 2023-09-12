import datetime as dt
from typing import Callable

import pytest
from django.test import RequestFactory, override_settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.request import Request
from rest_framework.response import Response

from rest_framework_api_key.models import APIKey
from rest_framework_api_key.permissions import BaseHasAPIKey, HasAPIKey, KeyParser

pytestmark = pytest.mark.django_db


@api_view()
@permission_classes([HasAPIKey])
def view(request: Request) -> Response:
    return Response()


def test_if_valid_api_key_then_permission_granted(rf: RequestFactory) -> None:
    _, key = APIKey.objects.create_key(name="test")
    authorization = f"Api-Key {key}"
    request = rf.get("/test/", HTTP_AUTHORIZATION=authorization)

    response = view(request)
    assert response.status_code == 200


def test_if_valid_api_key_custom_header_then_permission_granted(
    rf: RequestFactory,
) -> None:
    with override_settings(API_KEY_CUSTOM_HEADER="HTTP_X_API_KEY"):
        _, key = APIKey.objects.create_key(name="test")
        request = rf.get("/test/", HTTP_X_API_KEY=key)

        response = view(request)
        assert response.status_code == 200


def test_if_no_api_key_then_permission_denied(rf: RequestFactory) -> None:
    request = rf.get("/test/")

    response = view(request)
    assert response.status_code == 403


def _scramble_prefix(key: str) -> str:
    prefix, _, secret_key = key.partition(".")
    truncated_prefix = prefix[:-1]
    return truncated_prefix + "." + secret_key


@pytest.mark.parametrize(
    "modifier",
    [
        lambda _: "",
        lambda _: "abcd",
        lambda _: "foo.bar",
        lambda key: " " + key,
        lambda key: key.upper(),
        lambda key: key.lower(),
        lambda key: _scramble_prefix(key),
    ],
)
def test_if_invalid_api_key_then_permission_denied(
    rf: RequestFactory,
    modifier: Callable[[str], str],
) -> None:
    _, key = APIKey.objects.create_key(name="test")
    authorization = f"Api-Key {modifier(key)}"
    request = rf.get("/test/", HTTP_AUTHORIZATION=authorization)

    response = view(request)
    assert response.status_code == 403


@pytest.mark.parametrize(
    "authorization_fmt",
    [
        pytest.param("X-Key {key}", id="wrong-scheme"),
        pytest.param("Api-Key:{key}", id="not-space-separated"),
    ],
)
def test_if_malformed_authorization_then_permission_denied(
    rf: RequestFactory, authorization_fmt: str
) -> None:
    _, key = APIKey.objects.create_key(name="test")
    authorization = authorization_fmt.format(key=key)
    request = rf.get("/test/", HTTP_AUTHORIZATION=authorization)
    response = view(request)
    assert response.status_code == 403


def test_if_invalid_api_key_custom_header_then_permission_denied(
    rf: RequestFactory,
) -> None:
    with override_settings(API_KEY_CUSTOM_HEADER="HTTP_X_API_KEY"):
        request = rf.get("/test/", HTTP_X_API_KEY="doesnotexist")

        response = view(request)
        assert response.status_code == 403


def test_if_revoked_then_permission_denied(rf: RequestFactory) -> None:
    _, key = APIKey.objects.create_key(name="test", revoked=True)
    authorization = f"Api-Key {key}"
    request = rf.get("/test/", HTTP_AUTHORIZATION=authorization)

    response = view(request)
    assert response.status_code == 403


NOW = dt.datetime.now()
TOMORROW = NOW + dt.timedelta(days=1)
TWO_DAYS_AGO = NOW - dt.timedelta(days=2)


@pytest.mark.parametrize("expiry_date, ok", [(TOMORROW, True), (TWO_DAYS_AGO, False)])
def test_expiry_date(rf: RequestFactory, expiry_date: dt.datetime, ok: bool) -> None:
    _, key = APIKey.objects.create_key(name="test", expiry_date=expiry_date)
    authorization = f"Api-Key {key}"
    request = rf.get("/test/", HTTP_AUTHORIZATION=authorization)

    response = view(request)
    status_code = 200 if ok else 403
    assert response.status_code == status_code


def test_keyparser_keyword_override(rf: RequestFactory) -> None:
    class BearerKeyParser(KeyParser):
        keyword = "Bearer"

    class BearerHasAPIKey(BaseHasAPIKey):
        model = APIKey
        key_parser = BearerKeyParser()

    @api_view()
    @permission_classes([BearerHasAPIKey])
    def bearer_view(request: Request) -> Response:
        return Response()

    _, key = APIKey.objects.create_key(name="test")
    authorization = f"Bearer {key}"
    request = rf.get("/test/", HTTP_AUTHORIZATION=authorization)

    response = bearer_view(request)
    assert response.status_code == 200


def test_keyparser_lookup_exact_keyword(rf: RequestFactory) -> None:
    wrong_key = "My-Special-Api-Key 12345"
    request = rf.get("/test/", HTTP_AUTHORIZATION=wrong_key)
    assert KeyParser().get(request) is None
