# User Guide

## Getting started

### Installation

Install from PyPI:

```bash
pip install djangorestframework-api-key
```

**Note**: `djangorestframework-api-key` requires Django REST Framework >= 3.8.

### Project setup

Add the app to your `INSTALLED_APPS`:

```py
# settings.py

INSTALLED_APPS = [
  # ...
  'rest_framework',
  'rest_framework_api_key',
]
```

Run the included migrations:

```bash
python manage.py migrate
```

### Setting permissions

The `HasAPIKey` permission class protects a view behind API key authorization.

You can set the permission globally:

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

See also [Setting the permission policy](http://www.django-rest-framework.org/api-guide/permissions/#setting-the-permission-policy) for more information on using permission classes in the Django REST Framework.

!!! tip
    You can use the bitwise operators `|` and `&` to compose `HasAPIKey` with other permission classes and achieve more complex authorization behaviour.

    For example, to require a valid API key _or_ authentication credentials, use:

    ```python
    from rest_framework.permissions import IsAuthenticated
    from rest_framework_api_key.permissions import HasAPIKey
    # ...
    permission_classes = [HasAPIKey | IsAuthenticated]
    ```


### Making authorized requests

#### Authorization header

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
