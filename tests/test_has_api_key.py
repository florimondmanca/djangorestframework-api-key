"""Test the HasAPIKey permission class."""

import pytest

from rest_framework_api_key.permissions import HasAPIKey

pytestmark = pytest.mark.django_db


@pytest.fixture(name="view")
def fixture_view(view_with_permissions):
    return view_with_permissions(HasAPIKey)


def test_if_valid_api_key_then_permission_granted(create_request, view):
    request = create_request()
    response = view(request)
    assert response.status_code == 200


def test_if_no_api_key_then_permission_denied(create_request, view):
    request = create_request(authorization=None)
    response = view(request)
    assert response.status_code == 403


@pytest.mark.parametrize(
    "authorization",
    [
        "foo",
        "Content-Type: text/plain",
        "Api-Key:",
        "Api-Key abcd",
        "Api-Key foo:bar",
        "Api Key {key}",
        "Api-Key: {key}",
        "{key}",
    ],
)
def test_if_invalid_api_key_then_permission_denied(
    create_request, view, authorization
):
    request = create_request(authorization=authorization)
    response = view(request)
    assert response.status_code == 403


def test_if_revoked_then_permission_denied(create_request, view):
    request = create_request(revoked=True)
    response = view(request)
    assert response.status_code == 403


def test_full_prefix_must_be_present(create_request, view):
    def get_authorization(key: str) -> str:
        prefix, secret_key = key.split(".")
        truncated_prefix = prefix[:-1]
        return "Api-Key " + truncated_prefix + "." + secret_key

    request = create_request(authorization=get_authorization)
    response = view(request)
    assert response.status_code == 403
