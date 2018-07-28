# djangorestframework-api-key [![travis][travis-image]][travis-url]

🔐 Web API permissions for the [Django REST Framework][rest-framework-url].

WORK IN PROGRESS

This project is based on (yet not a fork of) the unmaintained [django-rest-framework-api-key][django-rest-framework-api-key-url] project.

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

Django REST Framework: 3.8+

Python/Django:

- 3.4/1.11
- 3.4/2.0
- 3.5/1.11
- 3.5/2.0
- 3.6/1.11
- 3.6/2.0
- 3.7/2.0

**Note**: Python 3.7/Django 1.11 is not supported.

## Usage

### Permission classes

This package provides permission classes to allow external clients to use your API.

The `HasAPIKey` permission class requires **all clients** to provide a valid API key.

Note that this applies regardless of whether the client provides authentication credentials.

If you want to allow clients to provide either an API key or authentication credentials, use the utility `HasAPIKeyOrIsAuthenticated` permission class instead.

Refer to [Setting the permission policy][setting-the-permission-policy-url] for more information on using permission classes.

## Development

### Install

Installing locally requires [Pipenv][pipenv-url] and Python 3.7.

1. Fork the repo
2. Clone it on your local
3. Install dependencies with Pipenv: `$ pipenv install`
4. Activate using `$ pipenv shell`

### Tests

Run the tests using:

```bash
$ python runtests.py
```

### Generating migrations

```bash
$ python makemigrations.py
```

<!-- URLs -->

[rest-framework-url]: http://www.django-rest-framework.org

[pipenv-url]: https://github.com/pypa/pipenv

[setting-the-permission-policy-url]: http://www.django-rest-framework.org/api-guide/permissions/#setting-the-permission-policy

[django-rest-framework-api-key-url]: https://github.com/manosim/django-rest-framework-api-key

[travis-image]: https://travis-ci.org/florimondmanca/djangorestframework-api-key.svg?branch=master

[travis-url]: https://travis-ci.org/florimondmanca/djangorestframework-api-key
