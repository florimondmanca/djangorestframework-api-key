import typing

from django.conf import settings
from django.core.cache import cache

from .models import AbstractAPIKey


class CacheMixin:
    model: typing.Optional[typing.Type[AbstractAPIKey]] = None
    DEFAULT_CACHE_TIMEOUT = 60 * 60  # 1 hour
    API_KEY_CACHE_TIMEOUT = getattr(
        settings, "API_KEY_CACHE_TIMEOUT", DEFAULT_CACHE_TIMEOUT
    )

    @property
    def API_KEY_IS_CACHE_ENABLED(self) -> bool:
        return getattr(settings, "API_KEY_IS_CACHE_ENABLED", False)

    def get_cache_key_prefix(self) -> str:
        """
        Generate the prefix for the cache key. By default, it's based on the model name.
        """
        model = self.model if self.model else self.__class__.model
        if model is None:
            raise Exception("Model is not defined")
        return f"api_key_validity:{model.__name__}"

    def get_cache_key(self, key: str) -> str:
        """
        Generates the cache key based on the provided key.
        """
        return f"{self.get_cache_key_prefix()}:{key}"

    def get_from_cache(self, key: str) -> typing.Optional[bool]:
        """
        Fetches data from cache based on the provided key.
        """
        return cache.get(self.get_cache_key(key))

    def set_to_cache(self, key: str, value: bool) -> None:
        """
        Sets data in cache based on the provided key.
        """
        cache_key = self.get_cache_key(key)
        cache.set(cache_key, value, self.API_KEY_CACHE_TIMEOUT)
        prefix, _, _ = key.partition(".")
        cache.set(self.get_cache_key(prefix), cache_key, self.API_KEY_CACHE_TIMEOUT)

    def invalidate_cache(self, key: str) -> None:
        """
        Invalidates cache based on the provided key.
        """
        cache.delete(self.get_cache_key(key))

    def invalidate_cache_by_key_prefix(self, key_prefix: str) -> None:
        """
        Invalidates cache based on the provided key prefix.
        """
        key_prefix = self.get_cache_key(key_prefix)
        cache_key = cache.get(key_prefix)
        if cache_key:
            cache.delete(cache_key)
            cache.delete(key_prefix)
