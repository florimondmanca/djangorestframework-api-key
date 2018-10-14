from django.apps import AppConfig


class RestFrameworkApiKeyConfig(AppConfig):
    name = 'rest_framework_api_key'
    verbose_name = 'API Key Permissions'

    def ready(self):
        from . import checks
