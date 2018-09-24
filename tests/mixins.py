"""Test mixins."""

from django.contrib.auth import get_user_model
from rest_framework.test import APIRequestFactory, force_authenticate

from rest_framework_api_key.settings import (API_SECRET_KEY_HEADER,
                                             API_TOKEN_HEADER)

User = get_user_model()


class APIKeyTestMixin:
    """Mixin for testing APIKey permissions."""

    def setUp(self):
        self.factory = APIRequestFactory()

    def request(self, *, token=None, secret_key=None, user=None):
        """Create a test request."""
        kwargs = {}
        if token is not None:
            kwargs[API_TOKEN_HEADER] = token
        if secret_key is not None:
            kwargs[API_SECRET_KEY_HEADER] = secret_key
        request = self.factory.get('/test/', **kwargs)
        if user:
            force_authenticate(request, user=user)
        return request

    def assertPermissionDenied(self, view, **kwargs):
        request = self.request(**kwargs)
        response = view(request)
        self.assertEqual(response.status_code, 403)

    def assertPermissionGranted(self, view, **kwargs):
        request = self.request(**kwargs)
        response = view(request)
        self.assertEqual(response.status_code, 200)
