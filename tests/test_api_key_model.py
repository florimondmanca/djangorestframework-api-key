"""Test the APIKey model."""

from django.core.exceptions import ValidationError
from django.test import TestCase

from .factory import create_api_key


class APIKeyTest(TestCase):
    """Test the APIKey model."""

    def setUp(self):
        self.api_key = create_api_key()

    def test_token_generated_when_created(self):
        self.assertNotEqual(self.api_key.token, '')

    def test_hashed_token_generated_when_created(self):
        self.assertNotEqual(self.api_key.hashed_token, '')

    def test_token_long_enough(self):
        self.assertGreater(len(self.api_key.token), 16)

    def test_cannot_unrevoke(self):
        api_key = create_api_key(revoked=True)
        api_key.revoked = False
        with self.assertRaises(ValidationError):
            api_key.save()
        with self.assertRaises(ValidationError):
            api_key.clean()
