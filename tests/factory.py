"""APIKey factory for testing purposes."""

from rest_framework_api_key.models import APIKey


class APIKeyFactory:
    """Factory for APIKey objects."""

    def __init__(self):
        self.index = 0

    def __call__(self, **kwargs):
        """Create an APIKey object."""
        kwargs.setdefault('client_id', 'test_{}'.format(self.index))
        self.index += 1
        return APIKey.objects.create(**kwargs)


create_api_key = APIKeyFactory()
