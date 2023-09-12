import hashlib
import typing

from django.contrib.auth.hashers import (
    BasePasswordHasher,
    check_password,
    make_password,
)
from django.utils.crypto import constant_time_compare, get_random_string


def concatenate(left: str, right: str) -> str:
    return "{}.{}".format(left, right)


def split(concatenated: str) -> typing.Tuple[str, str]:
    left, _, right = concatenated.partition(".")
    return left, right


class Sha512ApiKeyHasher(BasePasswordHasher):
    """
    An API key hasher using the sha512 algorithm.

    This hasher should *NEVER* be used in Django's `PASSWORD_HASHERS` setting.
    It is insecure for use in hashing passwords, but is safe for hashing
    high entropy, randomly generated API keys.
    """

    algorithm = "sha512"

    def salt(self) -> str:
        """No need for a salt on a high entropy key."""
        return ""

    def encode(self, password: str, salt: str) -> str:
        if salt != "":
            raise ValueError("salt is unnecessary for high entropy API tokens.")
        hash = hashlib.sha512(password.encode()).hexdigest()
        return "%s$$%s" % (self.algorithm, hash)

    def verify(self, password: str, encoded: str) -> bool:
        encoded_2 = self.encode(password, "")
        return constant_time_compare(encoded, encoded_2)


class KeyGenerator:
    preferred_hasher = Sha512ApiKeyHasher()

    def __init__(self, prefix_length: int = 8, secret_key_length: int = 32):
        self.prefix_length = prefix_length
        self.secret_key_length = secret_key_length

    def get_prefix(self) -> str:
        return get_random_string(self.prefix_length)

    def get_secret_key(self) -> str:
        return get_random_string(self.secret_key_length)

    def hash(self, value: str) -> str:
        return make_password(value, hasher=self.preferred_hasher)

    def generate(self) -> typing.Tuple[str, str, str]:
        prefix = self.get_prefix()
        secret_key = self.get_secret_key()
        key = concatenate(prefix, secret_key)
        hashed_key = self.hash(key)
        return key, prefix, hashed_key

    def verify(self, key: str, hashed_key: str) -> bool:
        if self.using_preferred_hasher(hashed_key):
            # New simpler hasher
            result = self.preferred_hasher.verify(key, hashed_key)
        else:
            # Slower password hashers from Django
            # If verified, these will be transparently updated to the preferred hasher
            result = check_password(key, hashed_key)

        return result

    def using_preferred_hasher(self, hashed_key: str) -> bool:
        return hashed_key.startswith(f"{self.preferred_hasher.algorithm}$$")
