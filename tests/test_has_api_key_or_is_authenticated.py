"""Test the HasAPIKeyOrIsAuthenticated permission class."""

from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from rest_framework_api_key.permissions import HasAPIKeyOrIsAuthenticated

from .factory import create_api_key
from .mixins import APIKeyTestMixin
from .views import create_test_view

User = get_user_model()
view = create_test_view(HasAPIKeyOrIsAuthenticated)


class HasAPIKeyOrIsAuthenticatedTest(APIKeyTestMixin, APITestCase):
    """Test the HasAPIKeyOrIsAuthenticated permission class."""

    def setUp(self):
        super().setUp()
        self.user = User.objects.create_user(username='foo', password='bar')

    def test_if_authenticated_and_no_key_then_permission_granted(self):
        self.assertPermissionGranted(view, user=self.user)

    def test_if_authenticated_and_valid_key_then_permission_granted(self):
        api_key = create_api_key()
        self.assertPermissionGranted(view, user=self.user, token=api_key.token)

    def test_if_authenticated_and_revoked_key_then_permission_granted(self):
        api_key = create_api_key(revoked=True)
        self.assertPermissionGranted(view, user=self.user, token=api_key.token)
