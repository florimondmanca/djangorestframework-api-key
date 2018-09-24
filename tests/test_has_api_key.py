"""Test the HasAPIKey permission class."""

from rest_framework.test import APITestCase

from rest_framework_api_key.permissions import HasAPIKey

from .factory import create_api_key
from .mixins import APIKeyTestMixin
from .views import create_test_view

view = create_test_view(HasAPIKey)


class HasAPIKeyTest(APIKeyTestMixin, APITestCase):
    """Test the HasAPIKey permission class."""

    def test_if_no_token_then_permission_denied(self):
        self.assertPermissionDenied(
            view,
            token=None,
            secret_key='meh',
        )

    def test_if_no_secret_key_then_permission_denied(self):
        self.assertPermissionDenied(
            view,
            token='hol',
            secret_key=None,
        )

    def test_if_no_api_key_for_token_then_permission_denied(self):
        # No API key is database here, so token won't be found.
        self.assertPermissionDenied(
            view,
            token='foo',
            secret_key='meh',
        )

    def test_if_revoked_token_provided_then_permission_denied(self):
        api_key = create_api_key(revoked=True, secret_key='foo')
        wrong_secret_key = 'bar'
        self.assertPermissionDenied(
            view,
            token=api_key.token,
            secret_key=wrong_secret_key,
        )

    def test_if_valid_token_and_secret_key_then_permission_granted(self):
        secret_key = 'aab45fjdç9'  # Use a known secret key
        api_key = create_api_key(secret_key=secret_key)
        self.assertPermissionGranted(
            view,
            token=api_key.token,
            secret_key=secret_key,
        )
