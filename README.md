# djangorestframework-api-key

[![travis](https://img.shields.io/travis/florimondmanca/djangorestframework-api-key.svg)](https://travis-ci.org/florimondmanca/djangorestframework-api-key)
[![pypi](https://img.shields.io/pypi/v/djangorestframework-api-key.svg)][pypi-url]
[![python](https://img.shields.io/pypi/pyversions/djangorestframework-api-key.svg)][pypi-url]
[![django](https://img.shields.io/pypi/djversions/djangorestframework-api-key.svg?colorB=44b78b)][pypi-url]
[![drf](https://img.shields.io/badge/drf-3.8+-7f2d2d.svg)][pypi-url]
[![license](https://img.shields.io/pypi/l/djangorestframework-api-key.svg)][pypi-url]

[pypi-url]: https://pypi.org/project/djangorestframework-api-key/

🔐 API key permissions for the [Django REST Framework](http://www.django-rest-framework.org).

**Important**: Make sure to pin your dependency to `0.x` (i.e. `rest_framework_api_key < 1.0`). The upcoming 1.0 release will introduce a new (non-backwards compatible) API key scheme.

## Features

**`djangorestframework-api-key` allows server-side clients to safely use your API**.

Server-side clients are third-party backends and services which does not have a user account but still need to interact with your API in a secure way.

Intended to be:

- ✌️ **Simple to use**: create, view and revoke API keys via the admin site.
- 🔒 **As secure as possible**: secret keys are treated with the same level of care than passwords. They are hashed before being stored in the database and only visible at creation.

**Note**: there are important security aspects you need to consider before switching to an API key access control scheme. See [Security caveats](#caveats).

## Installation

- Install from PyPI:

```bash
$ pip install djangorestframework-api-key
```

- Add the app to your `INSTALLED_APPS`:

```python
# settings.py

INSTALLED_APPS = [
  # ...
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

This package provides the `HasAPIKey` permission class which requires clients to provide a valid API key.

As with every permission class, you can either set it globally:

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
    permission_classes = [HasAPIKey]
    # ...
```

Besides, you can use the bitwise operators `|` and `&` to compose `HasAPIKey` with other permission classes and achieve more complex authorization behaviour, e.g.:

- Require clients to pass a valid API key _AND_ their authentication credentials:

```python
permission_classes = [HasAPIKey & IsAuthenticated]
```

- Require clients to pass a valid API key _OR_ their authentication credentials:

```python
permission_classes = [HasAPIKey | IsAuthenticated]
```

See also [Setting the permission policy](http://www.django-rest-framework.org/api-guide/permissions/#setting-the-permission-policy) for more information on using permission classes.

### Making authorized requests

Once API key permissions are enabled on your API, clients can pass their API key via the `Api-Token` and `Api-Secret-Key` headers (this is customizable, see [Settings](#settings)):

```bash
$ curl -H 'Api-Token: YOUR_API_TOKEN_HERE' -H 'Api-Secret-Key: YOUR_API_SECRET_KEY_HERE' http://localhost:8000/my-resource/
```

To know under which conditions the access is granted, please see [Grant scheme](#grant-scheme).

### Creating and managing API keys

#### Admin site

When it is installed, `djangorestframework-api-key` adds an "API Key Permissions" section to the Django admin site where you can create, view and revoke API keys.

![](https://github.com/florimondmanca/djangorestframework-api-key/tree/master/img/admin-section.png)

## Settings

> Note: values of header settings should be set according to the behavior of [HttpRequest.META](https://docs.djangoproject.com/en/dev/ref/request-response/#django.http.HttpRequest.META). For example, `HTTP_API_KEY` maps to the `Api-Key` header.

`DRF_API_KEY_TOKEN_HEADER`:

- Name of the header which clients use to pass their API token.
- Default value: `"HTTP_API_TOKEN"`.

`DRF_API_KEY_SECRET_KEY_HEADER`:

- Name of the header which clients use the pass their API secret key.
- Default value: `"HTTP_API_SECRET_KEY"`.

## Security

### Generation scheme

An API key is made of two parts:

- The **API token**: a unique, generated, public string of characters.
- The **API secret key**: a unique, generated string of characters that the client must keep private.

For obvious security purposes, `djangorestframework-api-key` does not store the secret key at all on the server. The latter is shown only once to the client upon API key creation.

### Grant scheme

Access is granted if and only if all of the following is true:

1. The API key headers are present and correctly formatted (see [Making authorized requests](#making-authorized-requests)).
2. An unrevoked API key corresponding to the API token exists in the database.
3. The hash computed from the token and secret key matches the one of the API key.

### Caveats

[API keys ≠ Security](https://nordicapis.com/why-api-keys-are-not-enough/): depending on your situation, you should probably not rely on API keys only to authenticate/authorize your clients.

**Using API keys shifts the responsability of Information Security on your clients**. This induces risks, especially if detaining an API key gives access to confidential information or write operations. For example, an attacker could impersonate clients if their let their API key leak because of insufficient security measures.

As a best practice, you should apply the _Principle of Least Privilege_: allow only those who require resources to access those specific resources. In other words: **if your non-user client only needs to access a specific endpoint, add API permissions on that endpoint only**.

Act responsibly!

## Example project

An [example project](https://github.com/florimondmanca/djangorestframework-api-key/tree/master/example_project) shows usage in the context of a Django project.

## Changelog

See [CHANGELOG.md](https://github.com/florimondmanca/djangorestframework-api-key/tree/master/CHANGELOG.md).

## Contributing

See [CONTRIBUTING.md](https://github.com/florimondmanca/djangorestframework-api-key/tree/master/CONTRIBUTING.md).

## License

MIT
