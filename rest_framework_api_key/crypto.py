from typing import TYPE_CHECKING, Tuple

from django.contrib.auth.hashers import check_password, make_password
from django.utils.crypto import get_random_string

if TYPE_CHECKING:
    from .models import APIKey


class KeyGenerator:
    PREFIX_LENGTH = 8
    SECRET_KEY_LENGTH = 32

    def get_prefix(self) -> str:
        return get_random_string(self.PREFIX_LENGTH)

    def get_secret_key(self) -> str:
        return get_random_string(self.SECRET_KEY_LENGTH)

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
