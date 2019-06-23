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

Please refer to [HttpRequest.META](https://docs.djangoproject.com/en/2.2/ref/request-response/#django.http.HttpRequest.META) for more information on headers in Django.

### Creating and managing API keys

#### Admin site

When it is installed, `djangorestframework-api-key` adds an "API Key Permissions" section to the Django admin site where you can create, view and revoke API keys.

#### Programmatic usage

API keys can be created, viewed and revoked programmatically by manipulating the `APIKey` model.

> The examples below use the [Django shell](https://docs.djangoproject.com/en/2.2/ref/django-admin/#django-admin-shell).

- You can view and query `APIKey` like any other model. For example, to know the total number of API keys:

```python
>>> from rest_framework_api_key.models import APIKey
>>> APIKey.objects.count()
42
```

- If you wish to create an API key programmatically, you'll most likely want a one-time access to its generated key too. To do so, use the `.create_key()` method on the `APIKey` objects manager instead of `.create()`:

```python
>>> from rest_framework_api_key.models import APIKey
>>> api_key, key = APIKey.objects.create_key(name="my-remote-service")
>>> # Proceed with `api_key` and `key`...
```

!!! danger
    To prevent leaking API keys, you must only give the `key` **to the client that triggered its generation**. In particular, **do not keep any trace of it on the server**.

## Customization

This package provides various customization APIs that allow you to extend its basic behavior.

### API key models

If the built-in `APIKey` model doesn't fit your needs, you can create your own by subclassing `AbstractAPIKey`. This is particularly useful if you need to **store extra information** or **link API keys to other models** using a `ForeignKey` or a `ManyToManyField`.

#### Example

Here's how you could link API keys to an imaginary `Organization` model:

```python
# organizations/models.py
from django.db import models
from rest_framework_api_key.models import AbstractAPIKey

class Organization(models.Model):
    name = models.CharField(max_length=128)
    active = models.BooleanField(default=True)

class OrganizationAPIKey(AbstractAPIKey):
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name="api_keys",
    )
```

If you need to customize the model's `Meta`, it should inherit from `AbstractAPIKey.Meta`:

```python
class OrganizationAPIKey(AbstractAPIKey):
    # ...
    class Meta(AbstractAPIKey.Meta):
        verbose_name = "Organization API key"
        verbose_name_plural = "Organization API keys"
```

#### Migrations

Because `AbstractAPIKey` is an [abstract model](https://docs.djangoproject.com/en/2.2/topics/db/models/#abstract-base-classes), the custom API key model will have its own table in the database.

This means that you need to **generate a migration** and then **apply it** to be able to query the new API key model:

```bash
python manage.py makemigrations
python manage.py migrate
```

!!! important
    If `AbstractAPIKey` changes (e.g. because of an update to `djangorestframework-api-key`), you will need to **generate and apply migrations again** to account for these changes.

#### Managers

The `APIKey` model as well as custom API keys models inherited from `AbstractAPIKey` have a dedicated [manager](https://docs.djangoproject.com/en/2.2/topics/db/managers) which is responsible for implementing `.create_key()` and other important behavior.

As a result, if you want to build a custom API key manager, it should inherit from `BaseAPIKeyManager` instead of Django's `Manager`.

Besides [customization APIs that come with Django's managers](https://docs.djangoproject.com/en/2.2/topics/db/managers/#custom-managers), `BaseAPIKeyManager` gives you one extra hook: you can override `.get_usable_keys()` to customize which set of API keys clients can use in authorized requests.

For example, here's how to restrict usable keys to those of active organizations only:

```python
class OrganizationAPIKeyManager(BaseAPIKeyManager):
    def get_usable_keys(self):
        return super().get_usable_keys().filter(organization__active=True)
```

!!! check
    Note the call to the parent implementation using `super()` here. This is because `.get_usable_keys()` has some default behavior, including making sure that revoked API keys cannot be used.

!!! tip
    You don't need to use a custom model to use a custom manager — it can be used on the built-in `APIKey` model as well.

#### Admin panel

If you'd like to view and manage your custom API key model via the [Django admin site](https://docs.djangoproject.com/en/2.2/ref/contrib/admin/), you can create register a subclass of `APIKeyModelAdmin`:

```python
# organizations/admin.py
from django.contrib import admin
from rest_framework_api_key.admin import APIKeyModelAdmin
from .models import OrganizationAPIKey

@admin.register(OrganizationAPIKey)
class OrganizationAPIKeyModelAdmin(APIKeyModelAdmin):
    pass
```

You can also customize any of the default attributes given by `APIKeyModelAdmin`. For example, to allow to search organization API keys by organization name while keeping the original search behavior, you can write:

```python
    search_fields = [*APIKeyModelAdmin.search_fields, "organization__name"]
```

!!! question "Are model inlines supported?"
    Unfortunately, showing editable API keys in the related model via [inlines](https://docs.djangoproject.com/en/2.2/ref/contrib/admin/#inlinemodeladmin-objects) is **not supported**. This is due to limited customization of saving inline forms, which does not allow to correctly save and display the generated key.

### Permission classes

The built-in `HasAPIKey` permission class only checks against the built-in `APIKey` model. This means that if you use a custom API key model, you need to create a **custom permission class** for your application to validate API keys against it.

You can do so by subclassing `BaseHasAPIKey` and specifying the `.model` class attribute:

```python
# organizations/permissions.py
from rest_framework_api_key.permissions import BaseHasAPIKey
from .models import OrganizationAPIKey

class HasOrganizationAPIKey(BaseHasAPIKey):
    model = OrganizationAPIKey
```

You can then use `HasOrganizationAPIKey` as described in [Setting permissions](#setting-permissions).

!!! tip
    If you need to customize `.has_permission()` or `.has_object_permission()`, feel free to read the [source code](https://github.com/florimondmanca/djangorestframework-api-key/blob/master/rest_framework_api_key/permissions.py).

#### API key parsing

By default, API key permission classes retrieve the API key from the `Authorization` header or a custom header, as described in [Making authorized requests](#making-authorized-requests).

You can override this behavior by redefining the `.get_key()` method on your custom permission class. It accepts the [HttpRequest](https://docs.djangoproject.com/en/2.2/ref/request-response/#httprequest-objects) object as unique argument and should return the API key as an `str` if one was found, or `None` otherwise.

For example, here's how you could retrieve the API key from a cookie:

```python
class HasOrganizationAPIKey(BaseHasAPIKey):
    # ...
    def get_key(self, request):
        return request.COOKIES.get("api_key")
```

If your custom key parsing algorithm is complex, you may want to define it as a separate component. To do so, build a class which implements the `.get()` method with the same signature as `.get_key()`, and set it as the `.key_parser`:

```python
class CookieKeyParser:
    def get(self, request):
        cookie_name = getattr(settings, "API_KEY_COOKIE_NAME", "api_key")
        return request.COOKIES.get(cookie_name)

class HasOrganizationAPIKey(BaseHasAPIKey):
    # ...
    key_parser = CookieKeyParser()
```

### Key generation

!!! warning
    **This is an advanced topic**. Customizing the key generation algorithm must be done with care to prevent security issues.

    If you proceed, it is best to customize key generation **with a clean database state**, that is **before running initial migrations**, and more importantly **before any API key is created**.

This package ships with a key generation algorithm based on Django's password hashing infrastructure (see also [Security](security.md)).

The `.key_generator` attribute on `BaseAPIKeyManager` allows you to customize key generation.

For example,  you can customize the length of the prefix and secret key using:

```python
from rest_framework_api_key.models import BaseAPIKeyManager
from rest_framework_api_key.crypto import KeyGenerator

class OrganizationAPIKeyManager(BaseAPIKeyManager):
    key_generator = KeyGenerator(prefix_length=8, secret_key_length=32)  # Default values

class OrganizationAPIKey(AbstractAPIKey):
    objects = OrganizationAPIKeyManager()
    # ...
```

If you want to replace the key generation algorithm entirely, you can create your own `KeyGenerator` class. It must implement the `.generate()` and `.verify()` methods. At this point, it's probably best to read the [source code](https://github.com/florimondmanca/djangorestframework-api-key/blob/master/rest_framework_api_key/crypto.py) for the built-in `KeyGenerator`.

!!! check
    If the signature of your `.generate()` method is different from the built-in one, you'll need to override `.assign_key()` in your custom API key manager as well.
    
    Likewise, if `.verify()` must accept anything else than the `key` and `hashed_key`, you'll need to override `.is_valid()` on your custom API key model.
    
    See [models.py](https://github.com/florimondmanca/djangorestframework-api-key/blob/master/rest_framework_api_key/models.py) for the source code of `BaseAPIKeyManager`.
