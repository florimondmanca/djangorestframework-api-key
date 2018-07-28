"""Test the HasAPIKey permission class."""

from rest_framework.test import APITestCase

from rest_framework_api_key.permissions import HasAPIKey

from .factory import create_api_key
from .mixins import APIKeyTestMixin
from .views import create_test_view

view = create_test_view(HasAPIKey)


class HasAPIKeyTest(APIKeyTestMixin, APITestCase):
    """Test the HasAPIKey permission class."""

    def test_if_no_api_key_permission_denied(self):
        self.assertPermissionDenied(view)

    def test_if_invalid_api_key_provided_then_permission_denied(self):
        self.assertPermissionDenied(view, key='foo')

    def test_if_revoked_api_key_provided_then_permission_denied(self):
        api_key = create_api_key(revoked=True)
        self.assertPermissionDenied(view, key=api_key.key)

    def test_if_valid_api_key_provided_then_permission_granted(self):
        api_key = create_api_key()
        self.assertPermissionGranted(view, key=api_key.key)
