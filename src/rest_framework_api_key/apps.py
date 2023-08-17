from django.apps import AppConfig
from django.db.models.signals import post_delete, post_save


class RestFrameworkApiKeyConfig(AppConfig):
    name = "rest_framework_api_key"
    verbose_name = "API Key Permissions"

    def ready(self) -> None:
        from .models import AbstractAPIKey
        from .signals import invalidate_api_key_cache

        # Connect signal for each descendant model of AbstractAPIKey
        for subclass in AbstractAPIKey.__subclasses__():
            post_save.connect(invalidate_api_key_cache, sender=subclass)
            post_delete.connect(invalidate_api_key_cache, sender=subclass)
