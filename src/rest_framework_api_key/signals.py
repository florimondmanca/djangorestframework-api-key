import typing

from django.core.cache import cache
from django.db.models import Model
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from .models import AbstractAPIKey
from .permissions import CacheMixin


@receiver([post_save, post_delete], sender=AbstractAPIKey)
def invalidate_api_key_cache(
    sender: Model, instance: AbstractAPIKey, **kwargs: typing.Any
) -> None:
    """
    Invalidate cache whenever an API key is updated, deleted, or revoked.
    """
    print(instance.hashed_key)
    cache_key = CacheMixin().get_cache_key(instance.hashed_key)
    cache.delete(cache_key)
