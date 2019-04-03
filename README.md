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

- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Security](#security)
- [Example project](#example-project)

## Features

**`djangorestframework-api-key` allows server-side clients to safely use your API**.

Server-side clients are third-party backends and services which does not have a user account but still need to interact with your API in a secure way.

Intended to be:

- ✌️ **Simple to use**: create, view and revoke API keys via the admin site, or use built-in helpers to create API keys programmatically.
- 🔒 **As secure as possible**: API keys are treated with the same level of care than user passwords. They are hashed before being stored in the database and only visible at creation.

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

This package provides permission classes to allow external clients to use your API:

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
    permission_classes = [HasAPIKey]
    # ...
```

See [Setting the permission policy (DRF docs)](http://www.django-rest-framework.org/api-guide/permissions/#setting-the-permission-policy) for more information on using permission classes.

### Making authorized requests

Once API key permissions are enabled on your API, clients can pass their API key via the `Authorization` header. It must be formatted as follows:

```
Authorization: Api-Key ********
```

where `********` refers to the API key.

To know under which conditions the access is granted, please see [Grant scheme](#grant-scheme).

### Creating and managing API keys

#### Admin panel

When it is installed, `djangorestframework-api-key` adds an "API Key Permissions" section to the Django admin site where you can create, view and revoke API keys.

![](https://github.com/florimondmanca/djangorestframework-api-key/tree/master/example_project/media/admin-section.png)

![](https://github.com/florimondmanca/djangorestframework-api-key/tree/master/example_project/media/admin-form.png)

![](https://github.com/florimondmanca/djangorestframework-api-key/tree/master/example_project/media/admin-created.png)

(Screenshots were taken from the [example project](#example-project).)

#### Programmatic usage (advanced)

API keys can be created, viewed and revoked programmatically by manipulating the `APIKey` model.

> The examples below use the [Django shell](https://docs.djangoproject.com/en/2.1/ref/django-admin/#django-admin-shell).

- You can view and query `APIKey` like any other model. For example, to know the number of active (unrevoked) API keys:

```python
>>> from rest_framework_api_key.models import APIKey
>>> APIKey.objects.filter(revoked=False).count()
42
```

- If you wish to create an API key programmatically, you'll most likely want a one-time access to its generated key too. To do so, use the `.create_key()` method on the `APIKey` objects manager instead of `.create()`:

```python
>>> from rest_framework_api_key.models import APIKey
>>> api_key, generated_key = APIKey.objects.create_key(name="Backend API")
>>> # Proceed with `api_key` and `generated_key`...
```

**Danger**: to preserve confidentiality, only give the generated key to the client, and do not keep any trace of it on the server after that is done.

## Security

### Key generation scheme

An API key is composed of two items:

- A prefix `P`, which is a generated string of 8 characters.
- A secret key `SK`, which is a generated string of 32 characters.

The generated key that clients use to [make authorized requests](#making-authorized-requests) is `GK = P.SK`. It is treated with the same level of care than passwords:

- Only a hashed version is stored in the database. The hash is computed using the default [password hasher](https://docs.djangoproject.com/en/2.1/topics/auth/passwords/).
- The generated key is shown only once to the client upon API key creation.

### Grant scheme

Access is granted if and only if all of the following is true:

1. The `Authorization` header is present and correctly formatted (see [Making authorized requests](#making-authorized-requests)).
2. An unrevoked API key with the prefix of the given key exists in the database.
3. The hash of the given key matches that of the API key.

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
