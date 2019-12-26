import sys

from .__version__ import __version__
from .types import patch_django_models_generics

default_app_config = "rest_framework_api_key.apps.RestFrameworkApiKeyConfig"

__all__ = ["__version__", "default_app_config"]

if sys.version_info >= (3, 7):
    patch_django_models_generics()

# Cleanup.
del sys
del patch_django_models_generics
