import pytest
from django.test import RequestFactory, override_settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.request import Request
from rest_framework.response import Response

from rest_framework_api_key.mixins import CacheMixin
from rest_framework_api_key.models import APIKey
from rest_framework_api_key.permissions import HasAPIKey

pytestmark = pytest.mark.django_db


@api_view()
@permission_classes([HasAPIKey])
def view(request: Request) -> Response:
    return Response()


def test_api_key_cache_without_caching(rf: RequestFactory) -> None:
    api_key, generated_key = APIKey.objects.create_key(name="test")
    authorization = f"Api-Key {generated_key}"
    request = rf.get("/test/", HTTP_AUTHORIZATION=authorization)

    response = view(request)
    assert response.status_code == 200
    assert HasAPIKey().get_from_cache(generated_key) is None


def test_api_key_cache_with_caching(rf: RequestFactory) -> None:
    with override_settings(API_KEY_IS_CACHE_ENABLED=True):
        api_key, generated_key = APIKey.objects.create_key(name="test")
        authorization = f"Api-Key {generated_key}"
        request = rf.get("/test/", HTTP_AUTHORIZATION=authorization)

        response = view(request)
        assert response.status_code == 200
        assert HasAPIKey().get_from_cache(generated_key) is True


def test_api_key_cache_invalidated_on_save() -> None:
    with override_settings(API_KEY_IS_CACHE_ENABLED=True):
        api_key, generated_key = APIKey.objects.create_key(name="test")
        assert (
            api_key.is_valid(generated_key) is True
        )  # First check, should not be cached
        cache_mixin = CacheMixin()
        cache_mixin.model = APIKey
        cache_mixin.set_to_cache(generated_key, True)
        assert cache_mixin.get_from_cache(generated_key) is True

        api_key.revoked = True
        api_key.save()

        # The cache should now be invalidated
        assert cache_mixin.get_from_cache(generated_key) is None


def test_api_key_cache_invalidated_on_delete() -> None:
    with override_settings(API_KEY_IS_CACHE_ENABLED=True):
        api_key, generated_key = APIKey.objects.create_key(name="test")
        assert (
            api_key.is_valid(generated_key) is True
        )  # First check, should not be cached
        cache_mixin = CacheMixin()
        cache_mixin.model = APIKey
        cache_mixin.set_to_cache(generated_key, True)
        assert cache_mixin.get_from_cache(generated_key) is True

        api_key.delete()

        # The cache should now be invalidated
        assert cache_mixin.get_from_cache(generated_key) is None
