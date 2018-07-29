# djangorestframework-api-key [![travis][travis-image]][travis-url]

🔐 Web API permissions for the [Django REST Framework][rest-framework-url].

This project is based on (yet not a fork of) the unmaintained [django-rest-framework-api-key][django-rest-framework-api-key-url] project.

## Supported versions

- Python: 3.4, 3.5, 3.6, 3.7
- Django: 1.11 (not on Python 3.7), 2.0
- Django REST Framework: 3.8+

## Features

Allow clients that are not supposed to have a user account (e.g. external services) to safely use your API.

Intended to be:

- 🚀 **Simple to use**: create, manage and revoke API keys via the admin site.
- 🔒 **Safe**: the key is only visible at creation and never shown again.

## Caveats

[API Keys ≠ Security](https://nordicapis.com/why-api-keys-are-not-enough/): depending on your situation, you should probably not rely on API keys only to authenticate/authorize your clients. Doing so shifts the responsability of information security on your clients. This induces risks, especially if detaining an API key gives access to confidential information or write operations.

As a general advice, **allow only those who require resources to access those specific resources**. If your non-user client only needs to access a specific endpoint, add API permissions on that endpoint only.

## Install

- Install from PyPI:

```bash
$ pip install djangorestframework-api-key
```

- Add the app to your `INSTALLED_APPS`:

```python
# settings.py

INSTALLED_APPS = [
  # ...,
  'rest_framework',
  'rest_framework_api_key',
]
```

Run the included migrations:

```bash
$ python manage.py migrate
```

## Usage

### Set permission classes

This package provides permission classes to allow external clients to use your API.

The `HasAPIKey` permission class requires **all clients** to provide a valid API key, regardless of whether they provide authentication details.

If you want to allow clients to provide either an API key or authentication credentials, use the utility `HasAPIKeyOrIsAuthenticated` permission class instead.

As with every permission class, you can either use them globally:

```python
# settings.py

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework_api_key.HasAPIKey',
    ]
}
```

or on a per-view basis:

```python
# views.py
from rest_framework_api_key.permissions import HasAPIKey
from rest_framework.views import APIView

class UserListView(APIView):
    permission_classes = (HasAPIKey,)
    # ...
```

Refer to [DRF Docs - Setting the permission policy][setting-the-permission-policy-url] for more information on using permission classes.

### Make authorized requests

Once API key permissions are enabled on your API, clients can pass their API key via the `Api-Key` header (this is customizable, see [Settings](#settings)):

```bash
$ curl -H 'Api-Key: YOUR_API_KEY_HERE' http://localhost:8000/my-resource/
```

### Settings

`API_KEY_HEADER`:

- Name of the header which clients use to pass their API key.
- Default value: `HTTP_API_KEY` (which means clients should use the `Api-Key` header — see the [docs on HttpRequest.META](https://docs.djangoproject.com/en/dev/ref/request-response/#django.http.HttpRequest.META)).

### Example project

See the [example project][example-project-url] for example usage in the context of a Django project.

## Development

### Install

Installing locally requires [Pipenv][pipenv-url] and Python 3.7.

1. Fork the repo
2. Clone it on your local
3. Install dependencies with Pipenv: `$ pipenv install --dev`
4. Activate using `$ pipenv shell`

### Tests

Run the tests using:

```bash
$ python runtests.py
```

### Generating migrations

This package includes migrations. To update them in case of changes without setting up a Django project, run:

```bash
$ python makemigrations.py rest_framework_api_key
```

### CI/CD - Releases

Travis CI is in use to automatically:

- Test the package on supported versions of Python and Django.
- Release tagged commits to PyPI

See `.travis.yml` for further details.


<!-- URLs -->

[example-project-url]: https://github.com/florimondmanca/djangorestframework-api-key-example

[rest-framework-url]: http://www.django-rest-framework.org

[pipenv-url]: https://github.com/pypa/pipenv

[setting-the-permission-policy-url]: http://www.django-rest-framework.org/api-guide/permissions/#setting-the-permission-policy

[django-rest-framework-api-key-url]: https://github.com/manosim/django-rest-framework-api-key

[travis-image]: https://travis-ci.org/florimondmanca/djangorestframework-api-key.svg?branch=master

[travis-url]: https://travis-ci.org/florimondmanca/djangorestframework-api-key
