try:
    import django
except ImportError:  # pragma: no cover
    pass
else:
    if django.VERSION < (3, 2):  # pragma: no cover
        default_app_config = "rest_framework_api_key.apps.RestFrameworkApiKeyConfig"

__version__ = "3.0.0"

__all__ = ["__version__", "default_app_config"]
