import pytest
from django.conf.global_settings import PASSWORD_HASHERS
from django.test import override_settings
from rest_framework import generics, permissions
from rest_framework.response import Response

from rest_framework_api_key.permissions import HasAPIKey

pytestmark = pytest.mark.django_db


@pytest.fixture(name="view")
def fixture_view(view_with_permissions):
    return view_with_permissions(HasAPIKey)


def test_if_valid_api_key_then_permission_granted(create_request, view):
    request = create_request()
    response = view(request)
    assert response.status_code == 200


@pytest.mark.parametrize("hasher", PASSWORD_HASHERS)
def test_hashers(create_request, view, hasher):
    with override_settings(PASSWORD_HASHERS=[hasher]):
        test_if_valid_api_key_then_permission_granted(create_request, view)


def test_if_no_api_key_then_permission_denied(create_request, view):
    request = create_request(authorization=None)
    response = view(request)
    assert response.status_code == 403


def _scramble_prefix(key: str) -> str:
    prefix, _, secret_key = key.partition(".")
    truncated_prefix = prefix[:-1]
    return truncated_prefix + "." + secret_key


@pytest.mark.parametrize(
    "modifier",
    [
        lambda key: "",
        lambda key: "abcd",
        lambda key: "foo.bar",
        lambda key: " " + key,
        str.upper,
        str.lower,
        _scramble_prefix,
    ],
)
def test_if_invalid_api_key_then_permission_denied(
    create_request, view, backend, modifier
):
    def get_authorization(key):
        return backend["default"].format(key=modifier(key))

    request = create_request(authorization=get_authorization)
    response = view(request)
    assert response.status_code == 403


def test_if_revoked_then_permission_denied(create_request, view):
    request = create_request(revoked=True)
    response = view(request)
    assert response.status_code == 403


def test_object_permission(create_request):
    class DenyObject(permissions.BasePermission):
        def has_object_permission(self, request, view, obj):
            return False

    class View(generics.GenericAPIView):
        permission_classes = [HasAPIKey | DenyObject]

        def get(self, request):
            self.check_object_permissions(request, object())
            return Response()

    view = View.as_view()

    request = create_request(authorization=None)
    response = view(request)
    assert response.status_code == 403
