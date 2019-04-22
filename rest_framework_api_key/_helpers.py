from typing import TYPE_CHECKING, Tuple

from django.contrib.auth.hashers import check_password, make_password
from django.utils.crypto import get_random_string

if TYPE_CHECKING:
    from .models import APIKey


_PREFIX_LENGTH = 8
_SECRET_KEY_LENGTH = 32


def generate_key() -> Tuple[str, str]:
    prefix = get_random_string(_PREFIX_LENGTH)
    secret_key = get_random_string(_SECRET_KEY_LENGTH)

    key = prefix + "." + secret_key  # for the client
    key_id = prefix + "." + make_password(key)  # for database storage

    return key, key_id


def check_key(key: str, hashed_key: str) -> bool:
    return check_password(key, hashed_key)

