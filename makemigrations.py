"""Script to run a stand-alone equivalent of `makemigrations`."""

import django
from django.conf import settings
from django.core.management import call_command


def makemigrations(app_name):
    """Make migrations for the given app."""
    DJANGO_SETTINGS = {
        'INSTALLED_APPS': (app_name,)
    }
    settings.configure(**DJANGO_SETTINGS)
    django.setup()
    call_command('makemigrations', app_name)


if __name__ == '__main__':
    makemigrations('rest_framework_api_key')
