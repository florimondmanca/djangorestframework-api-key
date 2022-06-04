import django

from .__version__ import __version__

if django.VERSION < (3, 2):  # pragma: no cover
    default_app_config = "rest_framework_api_key.apps.RestFrameworkApiKeyConfig"

__all__ = ["__version__", "default_app_config"]
