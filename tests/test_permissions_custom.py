import typing

import pytest
from test_project.heroes.models import Hero, HeroAPIKey
from test_project.heroes.permissions import HasHeroAPIKey

pytestmark = pytest.mark.django_db


@pytest.fixture(name="view")
def fixture_view(view_with_permissions: typing.Callable) -> typing.Callable:
    return view_with_permissions(HasHeroAPIKey)


@pytest.fixture(name="create_hero_request")
def fixture_create_hero_request(
    build_create_request: typing.Callable,
) -> typing.Callable:
    return build_create_request(HeroAPIKey)


def test_non_hero_api_key_denied(
    create_request: typing.Callable, view: typing.Callable
) -> None:
    request = create_request()
    response = view(request)
    assert response.status_code == 403


def test_hero_api_key_granted(
    create_hero_request: typing.Callable, view: typing.Callable
) -> None:
    hero = Hero.objects.create()
    hero_request = create_hero_request(hero=hero)
    response = view(hero_request)
    assert response.status_code == 200


def test_retired_hero_denied(
    create_hero_request: typing.Callable, view: typing.Callable
) -> None:
    hero = Hero.objects.create(retired=True)
    hero_request = create_hero_request(hero=hero)
    response = view(hero_request)
    assert response.status_code == 403
