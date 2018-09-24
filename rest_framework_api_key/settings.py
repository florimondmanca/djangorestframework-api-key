"""rest_framework_api_key settings."""

from django.conf import settings

API_TOKEN_HEADER = getattr(settings, 'API_TOKEN_HEADER', 'HTTP_API_TOKEN')
API_SECRET_KEY_HEADER = getattr(settings, 'API_SECRET_KEY_HEADER',
                                'HTTP_API_SECRET_KEY')

# The hashing algorithm used to generate the secret key.
# 'default' means the default configured password hash algorithm is used.
SECRET_KEY_ALGORITHM = getattr(settings, 'SECRET_KEY_ALGORITHM', 'default')
