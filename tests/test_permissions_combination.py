import pytest
from django.contrib.auth import get_user_model
from django.test import RequestFactory
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.test import force_authenticate

from rest_framework_api_key.models import APIKey
from rest_framework_api_key.permissions import HasAPIKey

pytestmark = pytest.mark.django_db


@api_view()
@permission_classes([HasAPIKey | IsAuthenticated])
def view(request: Request) -> Response:
    return Response()


def test_if_authenticated_and_no_api_key_then_permission_granted(
    rf: RequestFactory,
) -> None:
    user = get_user_model().objects.create_user(username="foo", password="bar")

    request = rf.get("/test/")
    force_authenticate(request, user)

    response = view(request)
    assert response.status_code == 200, response.data


def test_if_authenticated_and_revoked_api_key_then_permission_granted(
    rf: RequestFactory,
) -> None:
    user = get_user_model().objects.create_user(username="foo", password="bar")

    _, key = APIKey.objects.create_key(name="test", revoked=True)
    authorization = f"Api-Key {key}"

    request = rf.get("/test/", HTTP_AUTHORIZATION=authorization)
    force_authenticate(request, user)

    response = view(request)
    assert response.status_code == 200, response.data
