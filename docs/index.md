<div align="center">
  <h1 style="margin-bottom: 0;">Django REST Framework API Key</h1>
  <p style="margin-top: 1em; margin-bottom: 2em; font-size: large;">
    API key permissions for
    <a href="https://www.django-rest-framework.org" alt="drf" target="_blank" rel="noreferrer">
      Django REST Framework
    </a>
  </p>
  <div>
    <a href="https://dev.azure.com/florimondmanca/public/_build/latest?definitionId=7&branchName=master" target="_blank" rel="noreferrer">
      <img src="https://dev.azure.com/florimondmanca/public/_apis/build/status/florimondmanca.djangorestframework-api-key?branchName=master" alt="build status"/>
    </a>
    <a href="https://codecov.io/gh/florimondmanca/djangorestframework-api-key">
      <img src="https://codecov.io/gh/florimondmanca/djangorestframework-api-key/branch/master/graph/badge.svg" alt="coverage">
    </a>
    <a href="https://pypi.org/project/djangorestframework-api-key" target="_blank" rel="noreferrer">
      <img src="https://badge.fury.io/py/djangorestframework-api-key.svg" alt="package version"/>
    </a>
  </div>
  <div>
    <img src="https://img.shields.io/pypi/pyversions/djangorestframework-api-key.svg" alt="python versions"/>
    <img src="https://img.shields.io/pypi/djversions/djangorestframework-api-key.svg?colorB=44b78b" alt="django versions"/>
    <img src="https://img.shields.io/badge/drf-3.8+-7f2d2d.svg" alt="drf versions"/>
  </div>
</div>

## Introduction

**Django REST Framework API Key is a powerful library for allowing server-side clients to safely use your API.** These clients are typically third-party backends and services (i.e. _machines_) which do not have a user account but still need to interact with your API in a secure way.

### Features

- ✌️ **Simple to use**: create, view and revoke API keys via the admin site, or use built-in helpers to create API keys programmatically.
- 🔒 **As secure as possible**: API keys are treated with the same level of care as user passwords. They are only visible at creation and hashed before storing in the database.
- 🎨 **Customizable**: satisfy specific business requirements by building your own customized API key models, permission classes and admin panels.

### Should I use API keys?

There are important security aspects you need to consider before switching to an API key access control scheme. We've listed some of these in [Security caveats](security.md#caveats), including serving your API over HTTPS.

Besides, see [Why and when to use API keys](https://cloud.google.com/endpoints/docs/openapi/when-why-api-key#top_of_page) for hints on whether API keys can fit your use case.

API keys are ideal in the following situations:

- Blocking anonymous traffic.
- Implementing API key-based [throttling](https://www.django-rest-framework.org/api-guide/throttling/). (Note that Django REST Framework already has many built-in utilities for this use case.)
- Identifying usage patterns by logging request information along with the API key.

They can also present enough security for authorizing internal services, such as your API server and an internal frontend application.

!!! warning
    Please note that this package is NOT meant for authentication. You should NOT use this package to identify individual users, either directly or indirectly.

    If you need server-to-server authentication, you may want to consider OAuth instead. Libraries such as [django-oauth-toolkit](https://django-oauth-toolkit.readthedocs.io/en/latest/index.html) can help.

## Quickstart

Install with `pip`:

```bash
pip install "djangorestframework-api-key==3.*"
```

!!! important
    It is highly recommended to **pin your dependency** to the latest major version (as depicted above), as breaking changes may and will happen between major releases.

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
