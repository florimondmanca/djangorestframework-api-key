import pytest
from django.core.cache import cache

from rest_framework_api_key.mixins import CacheMixin
from rest_framework_api_key.models import APIKey

pytestmark = pytest.mark.django_db


def test_api_key_cache_invalidated_on_save() -> None:
    api_key, generated_key = APIKey.objects.create_key(name="test")
    assert api_key.is_valid(generated_key) is True  # First check, should not be cached

    # Modify and save the API key
    api_key.revoked = True
    api_key.save()

    # The cache should now be invalidated
    cache_key = CacheMixin().get_cache_key(generated_key)
    assert cache.get(cache_key) is None


def test_api_key_cache_invalidated_on_delete() -> None:
    api_key, generated_key = APIKey.objects.create_key(name="test")
    assert api_key.is_valid(generated_key) is True  # First check, should not be cached

    # Delete the API key
    api_key.delete()

    # The cache should now be invalidated
    cache_key = CacheMixin().get_cache_key(generated_key)
    assert cache.get(cache_key) is None
