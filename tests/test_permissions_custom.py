import pytest
from django.test import RequestFactory
from rest_framework.decorators import api_view, permission_classes
from rest_framework.request import Request
from rest_framework.response import Response
from test_project.heroes.models import Hero, HeroAPIKey
from test_project.heroes.permissions import HasHeroAPIKey

from rest_framework_api_key.models import APIKey

pytestmark = pytest.mark.django_db


@api_view()
@permission_classes([HasHeroAPIKey])
def view(request: Request) -> Response:
    return Response()


def test_non_hero_api_key_denied(rf: RequestFactory) -> None:
    _, key = APIKey.objects.create_key(name="test")
    authorization = f"Api-Key {key}"
    request = rf.get("/test/", HTTP_AUTHORIZATION=authorization)

    response = view(request)
    assert response.status_code == 403


def test_hero_api_key_granted(rf: RequestFactory) -> None:
    hero = Hero.objects.create()
    _, key = HeroAPIKey.objects.create_key(name="test", hero=hero)
    authorization = f"Api-Key {key}"
    request = rf.get("/test/", HTTP_AUTHORIZATION=authorization)

    response = view(request)
    assert response.status_code == 200


def test_retired_hero_denied(rf: RequestFactory) -> None:
    hero = Hero.objects.create(retired=True)
    _, key = HeroAPIKey.objects.create_key(name="test", hero=hero)
    authorization = f"Api-Key {key}"
    request = rf.get("/test/", HTTP_AUTHORIZATION=authorization)

    response = view(request)
    assert response.status_code == 403
