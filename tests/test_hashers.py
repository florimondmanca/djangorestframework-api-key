import pytest

from rest_framework_api_key.crypto import Sha512ApiKeyHasher


def test_sha512hasher_encode() -> None:
    hasher = Sha512ApiKeyHasher()

    key = "test"
    hashed_key = hasher.encode(key, "")
    assert hasher.verify(key, hashed_key)
    assert not hasher.verify("not-test", hashed_key)


def test_sha512hasher_invalid_salt() -> None:
    hasher = Sha512ApiKeyHasher()
    with pytest.raises(ValueError):
        hasher.encode("test", "salt")
