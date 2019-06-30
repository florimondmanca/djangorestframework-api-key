import typing

import pytest

from rest_framework_api_key.models import APIKey, Scope
from rest_framework_api_key.permissions import HasAPIKeyWithScopes

pytestmark = pytest.mark.django_db


@pytest.fixture(name="view")
def fixture_view(view_with_permissions, hero_read: Scope):
    return view_with_permissions(
        HasAPIKeyWithScopes, required_scopes=[hero_read.label]
    )


def without_scopes(*_) -> typing.Tuple[APIKey, str]:
    api_key, key = APIKey.objects.create_key(name="test")
    return api_key, key


def with_scopes(*scopes: Scope) -> typing.Tuple[APIKey, str]:
    api_key, key = without_scopes()
    for scope in scopes:
        api_key.scopes.add(scope)
    return api_key, key


@pytest.mark.parametrize(
    "factory, status", [(without_scopes, 403), (with_scopes, 200)]
)
def test_scopes_permission(
    create_request,
    view,
    hero_read: Scope,
    factory: typing.Callable,
    status: str,
):
    _, key = factory(hero_read)
    request = create_request(key=key)
    response = view(request)
    assert response.status_code == status
