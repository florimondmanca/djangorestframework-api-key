"""rest_framework_api_key settings."""

from django.conf import settings

_NAMESPACE = 'DRF_API_KEY_'


def _get_setting(name, default=None):
    full_name = _NAMESPACE + name
    return getattr(settings, full_name, default)


TOKEN_HEADER = _get_setting('TOKEN_HEADER', 'HTTP_API_TOKEN')
SECRET_KEY_HEADER = _get_setting('SECRET_KEY_HEADER', 'HTTP_API_SECRET_KEY')

# The hashing algorithm used to generate the secret key.
# 'default' means the default configured password hash algorithm is used.
SECRET_KEY_ALGORITHM = _get_setting('SECRET_KEY_ALGORITHM', 'default')
