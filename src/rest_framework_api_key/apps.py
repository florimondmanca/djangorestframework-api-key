from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class RestFrameworkApiKeyConfig(AppConfig):
    name = "rest_framework_api_key"
    verbose_name = _("API Key Permissions")
