import pytest
from rest_framework.permissions import IsAuthenticated

from rest_framework_api_key.permissions import HasAPIKey
from .utils import create_view_with_permissions

pytestmark = pytest.mark.django_db


@pytest.fixture(name="view")
def fixture_view():
    return create_view_with_permissions(HasAPIKey | IsAuthenticated)


def test_if_authenticated_and_no_api_key_then_permission_granted(create_request, view):
    request = create_request(authenticated=True, authorization=None)
    response = view(request)
    assert response.status_code == 200, response.data


def test_if_authenticated_and_revoked_api_key_then_permission_granted(
    create_request, view
):
    request = create_request(authenticated=True, revoked=True)
    response = view(request)
    assert response.status_code == 200, response.data
