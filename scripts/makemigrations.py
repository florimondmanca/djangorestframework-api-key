"""A stand-alone equivalent of `python manage.py makemigrations`."""

import sys
import django
from django.conf import settings
from django.core.management import call_command


if __name__ == "__main__":
    APP = "rest_framework_api_key"
    settings.configure(
        INSTALLED_APPS=[
            "django.contrib.contenttypes",
            APP,
            "tests.project.heroes",
            "tests.project.events",
        ]
    )
    django.setup()
    call_command("makemigrations", *sys.argv[1:])
