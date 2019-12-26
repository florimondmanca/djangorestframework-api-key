import typing

import pytest
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from rest_framework_api_key.permissions import HasAPIKey

pytestmark = pytest.mark.django_db


@pytest.fixture(name="view")
def fixture_view(view_with_permissions: typing.Callable) -> typing.Callable:
    # See: https://github.com/typeddjango/djangorestframework-stubs/issues/37
    permission_class = HasAPIKey | IsAuthenticated  # type: ignore
    return view_with_permissions(permission_class)


def test_if_authenticated_and_no_api_key_then_permission_granted(
    create_request: typing.Callable[..., Request],
    view: typing.Callable[[Request], Response],
) -> None:
    request = create_request(authenticated=True, authorization=None)
    response = view(request)
    assert response.status_code == 200, response.data


def test_if_authenticated_and_revoked_api_key_then_permission_granted(
    create_request: typing.Callable[..., Request],
    view: typing.Callable[[Request], Response],
) -> None:
    request = create_request(authenticated=True, revoked=True)
    response = view(request)
    assert response.status_code == 200, response.data
