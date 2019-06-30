from django.apps import AppConfig
from django.core import checks
from django.db.models.signals import post_migrate

from .checks import check_models_scopes
from .management import create_scopes


class RestFrameworkApiKeyConfig(AppConfig):
    name = "rest_framework_api_key"
    verbose_name = "API Key Permissions"

    def ready(self):
        post_migrate.connect(
            create_scopes,
            dispatch_uid="rest_framework_api_key.management.create_scopes",
        )
        checks.register(check_models_scopes, checks.Tags.models)
