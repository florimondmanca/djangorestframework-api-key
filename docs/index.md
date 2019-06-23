<div align="center">
  <h1>djangorestframework-api-key</h1>
  <div>
    <a href="https://travis-ci.org/florimondmanca/djangorestframework-api-key">
      <img src="https://img.shields.io/travis/florimondmanca/djangorestframework-api-key.svg" alt="build status"/>
    </a>
    <a href="https://pypi.org/project/djangorestframework-api-key">
      <img src="https://badge.fury.io/py/djangorestframework-api-key.svg" alt="package version"/>
    </a>
    <a href="https://github.com/ambv/black">
      <img src="https://img.shields.io/badge/code_style-black-000000.svg" alt="code style">
    </a>
  </div>
  <div>
    <img src="https://img.shields.io/pypi/pyversions/djangorestframework-api-key.svg" alt="python versions"/>
    <img src="https://img.shields.io/pypi/djversions/djangorestframework-api-key.svg?colorB=44b78b" alt="django versions"/>
    <img src="https://img.shields.io/badge/drf-3.8+-7f2d2d.svg" alt="drf versions"/>
    <img src="https://img.shields.io/pypi/l/djangorestframework-api-key.svg" alt="license"/>
  </div>
</div>

## API key permissions for [Django REST Framework](http://www.django-rest-framework.org)

> Migrating from 0.x? Read the [release notes](https://github.com/florimondmanca/djangorestframework-api-key/tree/master/CHANGELOG.md#100).

**`djangorestframework-api-key` allows server-side clients to safely use your API**.

Server-side clients are third-party backends and services (i.e. _machines_) which do not have a user account but still need to interact with your API in a secure way.

Intended to be:

- ✌️ **Simple to use**: create, view and revoke API keys via the admin site, or use built-in helpers to create API keys programmatically.
- 🔒 **As secure as possible**: API keys are treated with the same level of care than user passwords. They are hashed using the default password hasher before being stored in the database, and only visible at creation.

> **Note**: there are important security aspects you need to consider before switching to an API key access control scheme. See [Security caveats](security.md#caveats).

## Quickstart

Install the latest version with `pip`:

```bash
pip install djangorestframework-api-key
```

Add the app to your `INSTALLED_APPS`:

```python
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

To learn how to configure permissions and manage API keys, read the [User Guide](guide.md).
