from typing import TYPE_CHECKING, Tuple

from django.contrib.auth.hashers import check_password, make_password
from django.utils.crypto import get_random_string

if TYPE_CHECKING:
    from .models import APIKey


def _encode(secret_key: str) -> str:
    return make_password(secret_key)


def create_secret_key() -> Tuple[str, str]:
    secret_key = get_random_string(32)
    encoded = _encode(secret_key)
    return secret_key, encoded


def check_secret_key(secret_key: str, encoded: str) -> bool:
    return check_password(secret_key, encoded)
