import typing

import pytest

from rest_framework_api_key.crypto import KeyGenerator, concatenate
from rest_framework_api_key.models import APIKey, BaseAPIKeyManager

pytestmark = pytest.mark.django_db


class LegacyKeyGenerator(KeyGenerator):
    """Pre-1.4 key generator."""

    def _legacy_generate(self) -> typing.Tuple[str, str]:
        prefix = self.get_prefix()
        secret_key = self.get_secret_key()
        key = concatenate(prefix, secret_key)
        hashed_key = concatenate(prefix, self.hash(key))
        return key, hashed_key

    generate = _legacy_generate  # type: ignore


@pytest.fixture(name="manager")
def fixture_manager() -> BaseAPIKeyManager:
    class Manager(BaseAPIKeyManager):
        key_generator = LegacyKeyGenerator()

    manager = Manager()
    manager.model = APIKey
    return manager


def test_manager_with_legacy_key_generator(manager: BaseAPIKeyManager) -> None:
    manager.create_key(name="test")
