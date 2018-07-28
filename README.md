# djangorestframework-api-key

🔐 Web API permissions for the [Django REST Framework](http://www.django-rest-framework.org).

WORK IN PROGRESS

This project is based on (yet not a fork of) the unmaintained [django-rest-framework-api-key](https://github.com/manosim/django-rest-framework-api-key) project.

## Install

- Install from PyPI:

```
$ pip install djangorestframework-api-key
```

- Add to your `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
  # ...,
  'rest_framework_api_key',
]
```

Run the included migrations:

```
$ python manage.py migrate
```

## Supported versions

- Python: 3.4, 3.5, 3.6, 3.7
- Django: 1.11, 2.0
- Django REST Framework: 3.8+

## Usage

### Permission classes

This package provides permission classes to allow external clients to use your API.

The `HasAPIKey` permission class requires **all clients** to provide a valid API key.

Note that this applies regardless of whether the client provides authentication credentials.

If you want to allow clients to provide either an API key or authentication credentials, use the utility `HasAPIKeyOrIsAuthenticated` permission class instead.

Refer to [Setting the permission policy](http://www.django-rest-framework.org/api-guide/permissions/#setting-the-permission-policy) for more information on using permission classes.

## Development

### Install

Installing locally requires [Pipenv](https://github.com/pypa/pipenv) and Python 3.7.

1. Fork the repo
2. Clone it on your local
3. Install dependencies with Pipenv: `$ pipenv install`
