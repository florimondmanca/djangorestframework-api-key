"""A stand-alone equivalent of `python manage.py makemigrations`."""
import pathlib
import sys

import django
from django.conf import settings
from django.core.management import call_command

root = pathlib.Path(__file__).parent.parent
sys.path.append(str(root))

if __name__ == "__main__":
    APP = "rest_framework_api_key"
    settings.configure(INSTALLED_APPS=[APP, "test_project.heroes"])
    django.setup()

    # For available options, see:
    # https://docs.djangoproject.com/en/3.0/ref/django-admin/#makemigrations
    options = sys.argv[1:]
    call_command("makemigrations", *options, APP, "heroes")
