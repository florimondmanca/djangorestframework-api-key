# djangorestframework-api-key

[![travis](https://img.shields.io/travis/florimondmanca/djangorestframework-api-key.svg)](https://travis-ci.org/florimondmanca/djangorestframework-api-key)
[![pypi](https://img.shields.io/pypi/v/djangorestframework-api-key.svg)][pypi-url]
[![python](https://img.shields.io/pypi/pyversions/djangorestframework-api-key.svg)][pypi-url]
[![django](https://img.shields.io/pypi/djversions/djangorestframework-api-key.svg?colorB=44b78b)][pypi-url]
[![drf](https://img.shields.io/badge/drf-3.8+-7f2d2d.svg)][pypi-url]
[![license](https://img.shields.io/pypi/l/djangorestframework-api-key.svg)][pypi-url]

[pypi-url]: https://pypi.org/project/djangorestframework-api-key/

🔐 API key permissions for the [Django REST Framework](http://www.django-rest-framework.org).

> Migrating from 0.x? Read the [release notes](https://github.com/florimondmanca/djangorestframework-api-key/tree/master/CHANGELOG.md#1.0.0).

- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Security](#security)
- [Example project](#example-project)

## Features

**`djangorestframework-api-key` allows server-side clients to safely use your API**.

Server-side clients are third-party backends and services (i.e. _machines_) which do not have a user account but still need to interact with your API in a secure way.

Intended to be:

- ✌️ **Simple to use**: create, view and revoke API keys via the admin site, or use built-in helpers to create API keys programmatically.
- 🔒 **As secure as possible**: API keys are treated with the same level of care than user passwords. They are hashed using the default password hasher before being stored in the database, and only visible at creation.

**Note**: there are important security aspects you need to consider before switching to an API key access control scheme. See [Security caveats](#caveats).

## Installation

- Install from PyPI:

```bash
pip install djangorestframework-api-key
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
python manage.py migrate
```

## Usage

### Setting permissions

This package provides an `HasAPIKey` permission class. It requires clients to provide a valid API key.

As any permission class, you can either set it globally:

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

**Tip**: you can use the bitwise operators `|` and `&` to compose `HasAPIKey` with other permission classes and achieve more complex authorization behaviour, e.g.:

- Require clients to pass a valid API key _AND_ their authentication credentials:

```python
permission_classes = [HasAPIKey & IsAuthenticated]
```

- Require clients to pass a valid API key _OR_ their authentication credentials:

```python
permission_classes = [HasAPIKey | IsAuthenticated]
```

See also [Setting the permission policy](http://www.django-rest-framework.org/api-guide/permissions/#setting-the-permission-policy) for more information on using permission classes in the Django REST Framework.

### Making authorized requests

#### `Authorization` header

By default, clients must pass their API key via the `Authorization` header. It must be formatted as follows:

```
Authorization: Api-Key ********
```

where `********` refers to the generated API key.

To know under which conditions access is granted, please see [Grant scheme](#grant-scheme).

#### Custom header

You can set the `API_KEY_CUSTOM_HEADER` setting to a non-`None` value to require clients to pass their API key in a custom header instead of the `Authorization` header.

This is useful if you plan to use API keys _AND_ an authentication scheme which already uses the `Authorization` header (e.g. token-based authentication).

For example, if you set:

```python
# settings.py
API_KEY_CUSTOM_HEADER = "HTTP_X_API_KEY"
```

then clients must make authorized requests using:

```
X-Api-Key: ********
```

where `********` refers to the generated API key.

Please refer to [HttpRequest.META](https://docs.djangoproject.com/en/2.1/ref/request-response/#django.http.HttpRequest.META) for more information on headers in Django.

### Creating and managing API keys

#### Admin site

When it is installed, `djangorestframework-api-key` adds an "API Key Permissions" section to the Django admin site where you can create, view and revoke API keys.

![](https://github.com/florimondmanca/djangorestframework-api-key/blob/master/img/admin-section.png?raw=true)

![](https://github.com/florimondmanca/djangorestframework-api-key/blob/master/example_project/media/admin-form.png?raw=true)

![](https://github.com/florimondmanca/djangorestframework-api-key/blob/master/example_project/media/admin-created.png?raw=true)

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

**Danger**: to preserve confidentiality, give the generated key **to the client only**, and **do not keep any trace of it** on the server afterwards.

## Security

### Key generation scheme

An API key is composed of two items:

- A prefix `P`, which is a generated string of 8 characters.
- A secret key `SK`, which is a generated string of 32 characters.

The generated key that clients use to [make authorized requests](#making-authorized-requests) is `GK = P.SK`. It is treated with the same level of care than passwords:

- Only a hashed version is stored in the database. The hash is computed using the default password hasher\* (see also [How Django stores passwords](https://docs.djangoproject.com/en/2.1/topics/auth/passwords/#how-django-stores-passwords)).
- The generated key is shown only once to the client upon API key creation.

\*All hashers provided by Django should be supported. `djangorestframework-api-key` is tested against the [default list of `PASSWORD_HASHERS`](https://docs.djangoproject.com/en/2.2/ref/settings/#std:setting-PASSWORD_HASHERS).

### Grant scheme

Access is granted if and only if all of the following is true:

1. The API key header is present and correctly formatted (see [Making authorized requests](#making-authorized-requests)).
2. An unrevoked API key with the prefix of the given key exists in the database.
3. The hash of the given key matches that of the API key.

### Caveats

[API keys ≠ Security](https://nordicapis.com/why-api-keys-are-not-enough/): depending on your situation, you should probably not rely on API keys only to authenticate/authorize your clients.

**Using API keys shifts the responsability of Information Security on your clients**. This induces risks, especially if detaining an API key gives access to confidential information or write operations. For example, an attacker could impersonate clients if they let their API keys leak.

As a best practice, you should apply the _Principle of Least Privilege_: allow only those who require resources to access those specific resources. In other words: **if your client needs to access an endpoint, add API permissions on that endpoint only** instead of the whole API.

Besides, it is highly recommended to serve the API over **HTTPS** to ensure the confidentiality of API keys passed in requests.

Act responsibly!

## Example project

The [example project](https://github.com/florimondmanca/djangorestframework-api-key/tree/master/example_project) shows usage in the context of a Django project.

## Changelog

See [CHANGELOG.md](https://github.com/florimondmanca/djangorestframework-api-key/tree/master/CHANGELOG.md).

## Contributing

See [CONTRIBUTING.md](https://github.com/florimondmanca/djangorestframework-api-key/tree/master/CONTRIBUTING.md).

## License

MIT
