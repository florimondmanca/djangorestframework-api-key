import pytest

from rest_framework.permissions import IsAuthenticated
from rest_framework_api_key.permissions import HasAPIKey

pytestmark = pytest.mark.django_db


@pytest.fixture(name="view")
def fixture_view(view_with_permissions):
    return view_with_permissions(HasAPIKey | IsAuthenticated)


def test_if_authenticated_and_no_key_then_permission_granted(
    create_request, view
):
    request = create_request(authenticated=True)
    response = view(request)
    assert response.status_code == 200


def test_if_authenticated_and_valid_key_then_permission_granted(
    create_request, create_api_key, view
):
    key = create_api_key(secret_key="foo")
    request = create_request(
        authenticated=True, token=key.token, secret_key="foo"
    )
    response = view(request)
    assert response.status_code == 200


def test_if_authenticated_and_revoked_key_then_permission_granted(
    create_request, create_api_key, view
):
    key = create_api_key(revoked=True, secret_key="foo")
    request = create_request(
        authenticated=True, token=key.token, secret_key="foo"
    )
    response = view(request)
    assert response.status_code == 200
