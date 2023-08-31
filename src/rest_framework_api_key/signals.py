import typing

from django.db.models import Model
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from .models import AbstractAPIKey
from .permissions import CacheMixin


@receiver([post_save, post_delete], sender=AbstractAPIKey)
def invalidate_api_key_cache(
    sender: Model, instance: typing.Any, **kwargs: typing.Any
) -> None:
    """
    Invalidate cache whenever an API key is updated, deleted, or revoked.
    """
    cache_mixin = CacheMixin()
    cache_mixin.model = sender
    cache_mixin.invalidate_cache_by_key_prefix(instance.prefix)
