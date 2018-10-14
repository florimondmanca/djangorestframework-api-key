"""API key system checks."""

from django.conf import settings
from django.core.checks import Error, register


def _get_deprecated_setting_error(source, target, id):
    return Error(
        'Setting {} has been deprecated in v0.3'.format(source),
        hint='Use the {} setting instead.'.format(target),
        obj=settings,
        id='rest_framework_api_key.{}'.format(id),
    )


@register()
def check_header_settings_for_deprecation(app_configs, **kwargs):
    """Check header settings.

    API Key header settings have been updated to use the DRF_API_KEY_*
    namespace in version 0.3.
    """
    errors = []
    if hasattr(settings, 'API_TOKEN_HEADER'):
        errors.append(
            _get_deprecated_setting_error(
                source='API_TOKEN_HEADER',
                target='DRF_API_KEY_TOKEN_HEADER',
                id='E001',
            )
        )
    if hasattr(settings, 'API_SECRET_KEY_HEADER'):
        errors.append(
            _get_deprecated_setting_error(
                source='API_SECRET_KEY_HEADER',
                target='DRF_API_KEY_SECRET_KEY_HEADER',
                id='E002',
            )
        )
    return errors
