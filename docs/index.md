<div align="center">
  <h1 style="margin-bottom: 0;">djangorestframework-api-key</h1>
  <p style="margin-top: 1em; margin-bottom: 2em; font-size: large;">
    API key permissions for
    <a href="https://www.django-rest-framework.org" alt="drf" target="_blank" rel="noreferrer">
      Django REST Framework
    </a>
  </p>
  <div>
    <a href="https://travis-ci.org/florimondmanca/djangorestframework-api-key" target="_blank" rel="noreferrer">
      <img src="https://img.shields.io/travis/florimondmanca/djangorestframework-api-key.svg" alt="build status"/>
    </a>
    <a href="https://pypi.org/project/djangorestframework-api-key" target="_blank" rel="noreferrer">
      <img src="https://badge.fury.io/py/djangorestframework-api-key.svg" alt="package version"/>
    </a>
    <a href="https://github.com/ambv/black" target="_blank" rel="noreferrer">
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

## Introduction

**`djangorestframework-api-key` is a powerful library for allowing server-side clients to safely use your API.** These clients are typically third-party backends and services (i.e. _machines_) which do not have a user account but still need to interact with your API in a secure way.

### Features

- ✌️ **Simple to use**: create, view and revoke API keys via the admin site, or use built-in helpers to create API keys programmatically.
- 🔒 **As secure as possible**: API keys are treated with the same level of care than user passwords. They are hashed using the default password hasher before being stored in the database, and only visible at creation.
- 🎨 **Customizable**: satisfy specific business requirements by building your own customized API key models, permission classes and admin panels.

!!! info
    There are important security aspects you need to consider before switching to an API key access control scheme. See [Security caveats](security.md#caveats).

### Example use cases

- Using the built-in `APIKey` model, you can generate an API key and embed it in your frontend app server so that only it can access your API.
- By customizing API key models and permissions, you can associate API keys to an entity (e.g. a user, person, organization…), and then build endpoints to allow them to manage their API keys.

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
  "rest_framework",
  "rest_framework_api_key",
]
```

Run the included migrations:

```bash
python manage.py migrate
```

To learn how to configure permissions and manage API keys, head to the [User Guide](guide.md).
