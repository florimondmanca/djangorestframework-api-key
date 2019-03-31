"""Cryptography utilities."""

import binascii
import os
from typing import TYPE_CHECKING, Tuple

from django.contrib.auth.hashers import make_password, check_password

if TYPE_CHECKING:
    from .models import APIKey


def _generate_secret_key() -> str:
    return binascii.hexlify(os.urandom(16)).decode()


def _encode(secret_key: str) -> str:
    return make_password(secret_key)


def create_secret_key() -> Tuple[str, str]:
    secret_key = _generate_secret_key()
    encoded = _encode(secret_key)
    return secret_key, encoded


def check_secret_key(secret_key: str, encoded: str) -> bool:
    return check_password(secret_key, encoded)

