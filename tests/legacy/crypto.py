from typing import Tuple
from rest_framework_api_key.crypto import concatenate, KeyGenerator


class LegacyKeyGenerator(KeyGenerator):
    """Pre-1.4 key generator."""

    def generate(self) -> Tuple[str, str, str]:
        prefix = self.get_prefix()
        secret_key = self.get_secret_key()
        key = concatenate(prefix, secret_key)
        hashed_key = concatenate(prefix, self.hash(key))
        return key, hashed_key
