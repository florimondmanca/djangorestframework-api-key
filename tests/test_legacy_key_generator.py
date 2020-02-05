from typing import Tuple

import pytest
from django.contrib.auth.hashers import make_password
from django.utils.crypto import get_random_string

from rest_framework_api_key.crypto import KeyGenerator
from rest_framework_api_key.models import APIKey, BaseAPIKeyManager

pytestmark = pytest.mark.django_db


class LegacyKeyGenerator(KeyGenerator):
    """
    Pre-1.4 key generator.

    The key generator interface was updated in v1.4 via:
    https://github.com/florimondmanca/djangorestframework-api-key/pull/62

    We must ensure that custom key generators created based on the pre-1.4 interface
    continue to work in 1.x.
    """

    def generate(self) -> Tuple[str, str]:  # type: ignore
        # NOTE: this method should replicate the behavior before #62, and
        # have no dependencies on the current `rest_framework_api_key` package.
        prefix = get_random_string(8)
        secret_key = get_random_string(32)
        key = prefix + "." + secret_key
        key_id = prefix + "." + make_password(key)
        return key, key_id


@pytest.fixture(name="manager")
def fixture_manager():
    class Manager(BaseAPIKeyManager):
        key_generator = LegacyKeyGenerator()

    manager = Manager()
    manager.model = APIKey
    return manager


def test_manager_with_legacy_key_generator(manager):
    manager.create_key(name="test")
