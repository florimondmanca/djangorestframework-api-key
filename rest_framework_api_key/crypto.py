"""Cryptography utilities."""

import binascii
import os

from django.contrib.auth.hashers import get_hasher

from .settings import SECRET_KEY_ALGORITHM


def _get_hasher(algorithm):
    if algorithm is None:
        algorithm = SECRET_KEY_ALGORITHM
    return get_hasher(algorithm=algorithm)


def _generate_token():
    """Return a random API access token."""
    return binascii.hexlify(os.urandom(16)).decode()


def _generate_secret_key(algorithm=None):
    """Return a random API secret key.

    For security purposes, the secret key must NEVER be stored on the server.
    """
    hasher = _get_hasher(algorithm)
    return hasher.salt()


def hash_token(token, secret_key, algorithm=None):
    """Hash an API access token.

    The token is hashed using a generated secret key as a salt.
    """
    hasher = _get_hasher(algorithm)
    return hasher.encode(token, salt=secret_key)


def assign_token(api_key, secret_key=None):
    """Assign a token and its hash to an API key.

    Parameters
    ----------
    api_key : APIKey or dict
    secret_key : str, optional
        If not given, a new secret key is generated.

    Returns
    -------
    secret_key : str
        The secret key used to create the hash.

    """
    if secret_key is None:
        secret_key = _generate_secret_key()

    token = _generate_token()
    hashed_token = hash_token(token, secret_key)

    def _setattr(field, value):
        if isinstance(api_key, dict):
            api_key[field] = value
        else:
            setattr(api_key, field, value)

    _setattr('token', token)
    _setattr('hashed_token', hashed_token)

    return secret_key
