import hashlib
import typing

from django.conf import settings
from django.contrib.auth.hashers import check_password, make_password
from django.utils.crypto import constant_time_compare, get_random_string


def concatenate(left: str, right: str) -> str:
    return "{}.{}".format(left, right)


def split(concatenated: str) -> typing.Tuple[str, str]:
    left, _, right = concatenated.partition(".")
    return left, right


def hash_key(algo: str, key: str, salt: str) -> str:
    hasher = getattr(hashlib, algo)
    hash_value = hasher(key.encode() + salt.encode()).hexdigest()
    return f"plain_{algo}$${hash_value}"


def check_hash(key: str, hashed_key: str, salt: str) -> bool:
    algo, _, hash_value = hashed_key.partition("$$")
    algo = algo.replace("plain_", "")
    hasher = getattr(hashlib, algo)
    return constant_time_compare(
        hasher(key.encode() + salt.encode()).hexdigest(), hash_value
    )


class KeyGenerator:
    def __init__(self, prefix_length: int = 8, secret_key_length: int = 32):
        self.prefix_length = prefix_length
        self.secret_key_length = secret_key_length

    def get_prefix(self) -> str:
        return get_random_string(self.prefix_length)

    def get_secret_key(self) -> str:
        return get_random_string(self.secret_key_length)

    def hash(self, value: str, salt: str) -> str:
        hash_algo = getattr(settings, "DRF_API_KEY_HASHING_ALGORITHM", None)
        if hash_algo:
            # the hash is salted with the prefix to prevent rainbow table attacks
            # (even though the key should be random enough to prevent that)
            return hash_key(hash_algo, value, salt)
        return make_password(value)

    def generate(self) -> typing.Tuple[str, str, str]:
        prefix = self.get_prefix()
        secret_key = self.get_secret_key()
        key = concatenate(prefix, secret_key)
        hashed_key = self.hash(key, prefix)
        return key, prefix, hashed_key

    def verify(self, key: str, hashed_key: str, prefix: str) -> bool:
        if hashed_key.startswith("plain_"):
            # this is a plain key
            return check_hash(key, hashed_key, prefix)

        return check_password(key, hashed_key)
