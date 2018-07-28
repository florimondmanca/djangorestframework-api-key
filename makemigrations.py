"""Script to run a stand-alone equivalent of `makemigrations`."""

import sys

import django
from django.conf import settings
from django.core.management import call_command


def makemigrations(app_name: str):
    """Make migrations for the given app."""
    DJANGO_SETTINGS = {
        'INSTALLED_APPS': (app_name,)
    }
    settings.configure(**DJANGO_SETTINGS)
    django.setup()
    call_command('makemigrations', app_name)


if __name__ == '__main__':
    try:
        app_name = sys.argv[1]
    except IndexError:
        sys.stderr.write('Usage: python makemigrations.py APP_NAME\n')
        sys.exit(1)
    else:
        makemigrations(app_name)
