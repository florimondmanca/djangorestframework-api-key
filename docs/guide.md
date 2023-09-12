# User Guide

## Getting started

### Installation

Install with `pip`:

```bash
pip install "djangorestframework-api-key==3.*"
```

_**Note**: It is highly recommended to **pin your dependency** to the latest major version (as depicted above), as breaking changes may and will happen between major releases._

### Project setup

Add the app to your `INSTALLED_APPS`:

```py
# settings.py

INSTALLED_APPS = [
  # ...
  "rest_framework",
  "rest_framework_api_key",
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
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework_api_key.permissions.HasAPIKey",
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

### Manually validating API keys
You can also manually validate an API key with the `APIKey` objects manager using the `is_valid()` method on the manager lke below. This is useful for validating API keys outside of a normal Django view, such as inside a websocket consumer from Django Channels.

```python
from rest_framework_api_key.permissions import APIKey

# this should be a string containing only the API key - remove any additional text like "Api-Key" if present
raw_key = "XXXXXXXX.XXXXXXXXXX"
is_valid_key = APIKey.objects.is_valid(raw_key)
```

### Making authorized requests

#### Authorization header

By default, clients must pass their API key via the `Authorization` header. It must be formatted as follows:

```
Authorization: Api-Key <API_KEY>
```

where `<API_KEY>` refers to the full generated API key (see [Creating and managing API keys](#creating-and-managing-api-keys) below).

To know under which conditions access is granted, please see [Grant scheme](security.md#grant-scheme).

If wanting to also customize the keyword used for parsing the Api-Key, please see [API key Custom Keyword](guide.md#api-key-custom-keyword)

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
X-Api-Key: <API_KEY>
```

where `<API_KEY>` refers to the full generated API key.

Please refer to [HttpRequest.META](https://docs.djangoproject.com/en/2.2/ref/request-response/#django.http.HttpRequest.META) for more information on headers in Django.

### Creating and managing API keys

#### Admin site

When it is installed, `djangorestframework-api-key` adds an "API Key Permissions" section to the Django admin site where you can create, view and revoke API keys.

!!! note
    Upon creating an API key from the admin, the full API key is shown only once in a success message banner. **This is what should be passed in authorization headers.** After creation, only the prefix of the API key is shown in the admin site, mostly for identification purposes. If you lose the full API key, you'll need to regenerate a new one.

#### Programmatic usage

API keys can be created, viewed, revoked, and validated programmatically by manipulating the `APIKey` model.

- You can validate API keys manually, see the "Manually validating API keys" section above.
  
!!! note
    The examples below use the [Django shell](https://docs.djangoproject.com/en/2.2/ref/django-admin/#django-admin-shell).

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

- To retrieve an `APIKey` instance based on its generated key (which is not stored in the database) use the `.get_from_key()` method on the `APIKey` objects manager instead of `.get()`. This is useful if you'd like to access an `APIKey` object from a view protected by a `HasAPIKey` permission.

```python
from rest_framework.views import APIView
from rest_framework_api_key.models import APIKey
from rest_framework_api_key.permissions import HasAPIKey

from .models import Project

class ProjectListView(APIView):
    permission_classes = [HasAPIKey]

    def get(self, request):
        """Retrieve a project based on the request API key."""
        key = request.META["HTTP_AUTHORIZATION"].split()[1]
        api_key = APIKey.objects.get_from_key(key)
        project = Project.objects.get(api_key=api_key)
```

## Customization

This package provides various customization APIs that allow you to extend its basic behavior.

### API key models

If the built-in `APIKey` model doesn't fit your needs, you can create your own by subclassing `AbstractAPIKey`. This is particularly useful if you need to **store extra information** or **link API keys to other models** using a `ForeignKey` or a `ManyToManyField`.

!!! warning
    Associating API keys to users, directly or indirectly, can present a security risk. See also: [Should I use API keys?](https://florimondmanca.github.io/djangorestframework-api-key/#should-i-use-api-keys).
 
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
    If `AbstractAPIKey` changes (e.g. because of an update to Django REST Framework API Key), you will need to **generate and apply migrations again** to account for these changes.

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

If you'd like to view and manage your custom API key model via the [Django admin site](https://docs.djangoproject.com/en/2.2/ref/contrib/admin/), you can create and register a subclass of `APIKeyModelAdmin`:

```python
# organizations/admin.py
from django.contrib import admin
from rest_framework_api_key.admin import APIKeyModelAdmin
from .models import OrganizationAPIKey

@admin.register(OrganizationAPIKey)
class OrganizationAPIKeyModelAdmin(APIKeyModelAdmin):
    pass
```

You can also customize any of the default attributes defined in `APIKeyModelAdmin`. For example, to display the organization's name in the list view, and allow searching `OrganizationAPIKey` instances by organization name while keeping the original search behavior, you can write:

```python
    list_display = [*APIKeyModelAdmin.list_display, "organization__name"]
    search_fields = [*APIKeyModelAdmin.search_fields, "organization__name"]
```

!!! question "How can I display API keys on the detail page of a related model instance?"
    In theory, this could be done using Django's [`InlineModelAdmin`](https://docs.djangoproject.com/en/2.2/ref/contrib/admin/#inlinemodeladmin-objects).

    However, due to the limitations of inlines, this cannot be easily achieved while correctly saving and displaying the generated key in the detail page of the related model.

    As an alternative, you can use the `.list_filter` class attribute to filter API keys by an identifying field on the related model. In the examples above, you could use `organization__name` to filter API keys by organization.

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
    If you need to customize `.has_permission()` or `.has_object_permission()`, feel free to read the [source code](https://github.com/florimondmanca/djangorestframework-api-key/blob/master/src/rest_framework_api_key/permissions.py).

#### API key parsing

By default, API key permission classes retrieve the API key from the `Authorization` header or a custom header, as described in [Making authorized requests](#making-authorized-requests).

You can customize or override this behavior in several ways.

If you are building an API for an application you do not control that requires a specific header keyword, e.g. a client that sends API keys using the `Bearer` keyword as follows:

```
Authorization: Bearer <API_KEY>
```

Then you can subclass `KeyParser` with a custom `keyword`, and attach it to a custom permission class, like so:

```python
# settings.py
from rest_framework_api_key.models import HasAPIKey
from rest_framework_api_key.permissions import BaseHasAPIKey, KeyParser

class BearerKeyParser(KeyParser):
    keyword = "Bearer"

class HasAPIKey(BaseHasAPIKey):
    model = APIKey  # Or a custom model
    key_parser = BearerKeyParser()
```

You can also override the default header-based parsing completely.

To do so, redefine the `.get_key()` method on your custom permission class. This method accepts the [HttpRequest](https://docs.djangoproject.com/en/2.2/ref/request-response/#httprequest-objects) object as unique argument and should return the API key as an `str` if one was found, or `None` otherwise.

For example, here's how you could retrieve the API key from a cookie:

```python
class HasAPIKey(BaseHasAPIKey):
    model = APIKey  # Or a custom model

    def get_key(self, request):
        return request.COOKIES.get("api_key")
```

If your custom key parsing algorithm is more complex, you may want to define it as a separate component. To do so, build a key parser class, which must implement the `.get()` method with the same signature as `.get_key()`, then set it as the `.key_parser`, as follows:

```python
class CookieKeyParser:
    def get(self, request):
        cookie_name = getattr(settings, "API_KEY_COOKIE_NAME", "api_key")
        return request.COOKIES.get(cookie_name)

class HasAPIKey(BaseHasAPIKey):
    model = APIKey  # Or a custom model
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

If you want to replace the key generation algorithm entirely, you can create your own `KeyGenerator` class. It must implement the `.generate()` and `.verify()` methods. At this point, it's probably best to read the [source code](https://github.com/florimondmanca/djangorestframework-api-key/blob/master/src/rest_framework_api_key/crypto.py) for the built-in `KeyGenerator`.

!!! check
    If the signature of your `.generate()` method is different from the built-in one, you'll need to override `.assign_key()` in your custom API key manager as well.
    
    Likewise, if `.verify()` must accept anything else than the `key` and `hashed_key`, you'll need to override `.is_valid()` on your custom API key model.
    
    See [models.py](https://github.com/florimondmanca/djangorestframework-api-key/blob/master/src/rest_framework_api_key/models.py) for the source code of `BaseAPIKeyManager`.

## Typing support

This package provides type information starting with version 2.0, making it suitable for usage with type checkers such as `mypy`.

For the best experience, you may want to install packages such as [`django-stubs`](https://github.com/typeddjango/django-stubs) and [`djangorestframework-stubs`](https://github.com/typeddjango/djangorestframework-stubs). Note however that a seamless integration with these packages is not guaranteed yet.
