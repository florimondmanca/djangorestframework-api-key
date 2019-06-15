from typing import TYPE_CHECKING, Tuple

from django.contrib.auth.hashers import check_password, make_password
from django.utils.crypto import get_random_string

if TYPE_CHECKING:
    from .models import APIKey


class KeyGenerator:
    def __init__(self, prefix_length: int = 8, secret_key_length: int = 32):
        self.prefix_length = prefix_length
        self.secret_key_length = secret_key_length

    def get_prefix(self) -> str:
        return get_random_string(self.prefix_length)

    def get_secret_key(self) -> str:
        return get_random_string(self.secret_key_length)

    @staticmethod
    def concatenate(left: str, right: str) -> str:
        return "{}.{}".format(left, right)

    def generate(self) -> Tuple[str, str]:
        prefix = self.get_prefix()
        secret_key = self.get_secret_key()
        key = self.concatenate(prefix, secret_key)
        hashed_key = self.concatenate(prefix, make_password(key))
        return key, hashed_key

    def verify(self, key: str, hashed_key: str) -> bool:
        return check_password(key, hashed_key)
