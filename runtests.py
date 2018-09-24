"""
A standalone test runner script.

Configures the minimum settings required for djangorestframework-api-key's
tests to execute.

Uses an in-memory SQLite test database.
"""

import os
import sys


# Make sure the app is on the import path.
APP_DIR = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, APP_DIR)


SETTINGS_DICT = {
    'SECRET_KEY': 'abcdefg',
    'INSTALLED_APPS': (
        # Required because we using authentication during tests
        'django.contrib.auth',
        'django.contrib.sessions',
        'django.contrib.contenttypes',
        # Required for using the REST Framework
        'rest_framework',
        # Our app
        'rest_framework_api_key',
    ),
    # Required by Django
    'ROOT_URLCONF': 'tests.urls',
    'DATABASES': {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': ':memory:',
        },
    },
}


def run_tests(directory, verbosity=1):
    """Run tests located in the given directory."""
    # Configure Django settings
    from django.conf import settings
    settings.configure(**SETTINGS_DICT)

    # Initialize the app registry and other things
    import django
    django.setup()

    # Create a test runner
    from django.test.utils import get_runner
    TestRunner = get_runner(settings)

    # Run the tests and return the results.
    test_runner = TestRunner(verbosity=verbosity, interactive=True)
    failures = test_runner.run_tests([directory])
    sys.exit(failures)


if __name__ == '__main__':
    run_tests('tests')
