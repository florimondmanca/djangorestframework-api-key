# djangorestframework-api-key

[![travis](https://img.shields.io/travis/florimondmanca/djangorestframework-api-key.svg)](https://travis-ci.org/florimondmanca/djangorestframework-api-key)
[![pypi](https://img.shields.io/pypi/v/djangorestframework-api-key.svg)][pypi-url]
[![python](https://img.shields.io/pypi/pyversions/djangorestframework-api-key.svg)][pypi-url]
[![django](https://img.shields.io/pypi/djversions/djangorestframework-api-key.svg?colorB=44b78b)][pypi-url]
[![drf](https://img.shields.io/badge/drf-3.8+-7f2d2d.svg)][pypi-url]
[![license](https://img.shields.io/pypi/l/djangorestframework-api-key.svg)][pypi-url]

[pypi-url]: https://pypi.org/project/djangorestframework-api-key/

🔐 API key permissions for the [Django REST Framework](http://www.django-rest-framework.org).

## Features

**`djangorestframework-api-key` allows server-side clients to safely use your API**.

Server-side clients are third-party backends and services which does not have a user account but still need to interact with your API in a secure way.

Intended to be:

- ✌️ **Simple to use**: create, manage and revoke API keys via the admin site.
- 🔒 **As secure as possible**: secret keys are generated through cryptographic methods. They are only visible at creation, never shown again and never stored in the database.

There are important security aspects you need to consider before switching to an API key access control scheme. See [Security](#security).

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

- Run the included migrations:

```bash
$ python manage.py migrate
```

## Usage

### Setting permissions

This package provides permission classes to allow external clients to use your API.

- `HasAPIKey`: this permission class requires **all clients** to provide a valid API key, regardless of whether they provide authentication details.
- `HasAPIKeyOrIsAuthenticated`: if you want to allow clients to provide either an API key or authentication credentials, use this permission class instead.

As with every permission class, you can either use them globally:

```python
# settings.py
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework_api_key.permissions.HasAPIKey',
    ]
}
```

or on a per-view basis:

```python
# views.py
from rest_framework.views import APIView
from rest_framework_api_key.permissions import HasAPIKey

class UserListView(APIView):
    permission_classes = (HasAPIKey,)
    # ...
```

Refer to [DRF Docs - Setting the permission policy](http://www.django-rest-framework.org/api-guide/permissions/#setting-the-permission-policy) for more information on using permission classes.

### Creating and managing API keys

`djangorestframework-api-key` provides a Django Admin interface to create, manage and revoke API keys.

See [Example project](#example-project) for details.

### Making authorized requests

Once API key permissions are enabled on your API, clients can pass their API key via the `Api-Token` and `Api-Secret-Key` headers (this is customizable, see [Settings](#settings)):

```bash
$ curl -H 'Api-Token: YOUR_API_TOKEN_HERE' -H 'Api-Secret-Key: YOUR_API_SECRET_KEY_HERE' http://localhost:8000/my-resource/
```

## Settings

> Note: values of header settings should be set according to the behavior of [HttpRequest.META](https://docs.djangoproject.com/en/dev/ref/request-response/#django.http.HttpRequest.META). For example, `HTTP_API_KEY` maps to the `Api-Key` header.

`DRF_API_KEY_TOKEN_HEADER`:

- Name of the header which clients use to pass their API token.
- Default value: `HTTP_API_TOKEN`.

`DRF_API_KEY_SECRET_KEY_HEADER`:

- Name of the header which clients use the pass their API secret key.
- Default value: `HTTP_API_SECRET_KEY`.

## Example project

An [example project](https://github.com/florimondmanca/djangorestframework-api-key/tree/master/example_project) shows usage in the context of a Django project.

## Security

### Generation scheme

An API key is made of two parts:

- The **API token**: a unique, generated, public string of characters.
- The **API secret key**: a unique, generated string of characters that the client must keep private.

For obvious security purposes, `djangorestframework-api-key` does not store the secret key at all on the server. The latter is shown only once to the client upon API key creation.

### Validation scheme

Upon generation, a hash of the token salted by the secret key is computed.

To verify their permissions, clients pass both the token and secret key. These are used to compute a hash that is compared with the one stored in database. Access is only granted if hashes match.

### Caveats

[API keys ≠ Security](https://nordicapis.com/why-api-keys-are-not-enough/): depending on your situation, you should probably not rely on API keys only to authenticate/authorize your clients. Doing so **shifts the responsability of Information Security on your clients**. This induces risks, especially if detaining an API key gives access to confidential information or write operations.

More specifically, although this package uses cryptographically secure API key generation and validation schemes, a malicious attacker will be able to impersonate clients if the latter leak their API key.

As a best practice, you should apply the Principle of Least Privilege: **allow only those who require resources to access those specific resources**. If your non-user client only needs to access a specific endpoint, add API permissions on that endpoint only.

Act responsibly.

## Changelog

See [CHANGELOG.md](https://github.com/florimondmanca/djangorestframework-api-key/blob/master/CHANGELOG.md).

## Contributing

See [CONTRIBUTING.md](https://github.com/florimondmanca/djangorestframework-api-key/blob/master/CONTRIBUTING.md).

## License

MIT
