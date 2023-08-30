import pytest
from django.conf import LazySettings

from rest_framework_api_key.crypto import KeyGenerator
from rest_framework_api_key.models import APIKey


@pytest.mark.parametrize("algorithm", ["sha256", "sha512", "blake2b"])
def test_hashing_algorithm_honors_setting(
    settings: LazySettings, algorithm: str
) -> None:
    settings.DRF_API_KEY_HASHING_ALGORITHM = algorithm
    _key, _prefix, hashed_key = KeyGenerator().generate()
    assert hashed_key.startswith(f"plain_{algorithm}$$")


@pytest.mark.parametrize("algorithm", ["sha256", "sha512", "blake2b"])
def test_hash_verify(settings: LazySettings, algorithm: str) -> None:
    settings.DRF_API_KEY_HASHING_ALGORITHM = algorithm
    key, prefix, hashed_key = KeyGenerator().generate()
    assert KeyGenerator().verify(key, hashed_key, prefix) is True


@pytest.mark.parametrize("update_algo", [True, False])
@pytest.mark.django_db
def test_hash_verify_with_update(settings: LazySettings, update_algo: bool) -> None:
    api_key, generated_key = APIKey.objects.create_key(name="test")
    assert not api_key.hashed_key.startswith("plain_")
    assert api_key.is_valid(generated_key) is True

    settings.DRF_API_KEY_HASHING_ALGORITHM = "blake2b"
    settings.DRF_API_KEY_HASH_AUTOUPDATE = update_algo

    assert api_key.is_valid(generated_key) is True
    assert api_key.hashed_key.startswith("plain_blake2b$$") is update_algo
    assert (
        api_key.is_valid(generated_key) is True
    ), "check still works after potential update"
