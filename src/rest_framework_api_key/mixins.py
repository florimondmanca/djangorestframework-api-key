import typing

from django.conf import settings
from django.core.cache import cache


class CacheMixin:
    DEFAULT_CACHE_TIMEOUT = 60 * 60  # 1 hour
    API_KEY_CACHE_TIMEOUT = getattr(
        settings, "API_KEY_CACHE_TIMEOUT", DEFAULT_CACHE_TIMEOUT
    )

    @classmethod
    def get_cache_key_prefix(cls) -> str:
        """
        Generate the prefix for the cache key. By default, it's based on the class name.
        """
        return f"api_key_validity:{cls.__name__}"

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
        cache.set(self.get_cache_key(key), value, self.API_KEY_CACHE_TIMEOUT)
