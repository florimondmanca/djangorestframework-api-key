from django.apps import AppConfig
from django.core import checks

from .checks import check_models_scopes


class RestFrameworkApiKeyConfig(AppConfig):
    name = "rest_framework_api_key"
    verbose_name = "API Key Permissions"

    def ready(self):
        checks.register(check_models_scopes, checks.Tags.models)
