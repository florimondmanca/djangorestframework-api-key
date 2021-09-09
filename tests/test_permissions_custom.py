import pytest
from test_project.heroes.models import Hero, HeroAPIKey
from test_project.heroes.permissions import HasHeroAPIKey

from .utils import create_view_with_permissions

pytestmark = pytest.mark.django_db


@pytest.fixture(name="view")
def fixture_view():
    return create_view_with_permissions(HasHeroAPIKey)


@pytest.fixture(name="create_hero_request")
def fixture_create_hero_request(build_create_request):
    return build_create_request(HeroAPIKey)


def test_non_hero_api_key_denied(create_request, view):
    request = create_request()
    response = view(request)
    assert response.status_code == 403


def test_hero_api_key_granted(create_hero_request, view):
    hero = Hero.objects.create()
    hero_request = create_hero_request(hero=hero)
    response = view(hero_request)
    assert response.status_code == 200


def test_retired_hero_denied(create_hero_request, view):
    hero = Hero.objects.create(retired=True)
    hero_request = create_hero_request(hero=hero)
    response = view(hero_request)
    assert response.status_code == 403
