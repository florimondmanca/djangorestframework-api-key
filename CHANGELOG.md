# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.0.0]

Released: 2019-04-24

**This release is incompatible with 0.x**. It introduces a new and more transparent API key generation and validation scheme which allows to pass it in a single header, instead of two previously.

### Migrating from 0.x

Unfortunately, we could not provide a migration that would preserve existing API keys. This is because the cryptographic generation and validation methods have changed, which means new keys cannot be inferred from existing ones.

As a result, **all existing API keys will be destroyed** during Step 1) described below. You will need to regenerate them and notify your clients.

To migrate from 0.x, please follow these steps:

1. **Before upgrading**, reset migrations (_this will destroy existing API keys_):

```bash
python manage.py migrate rest_framework_api_key zero
```

2. Upgrade:

```bash
pip install -U djangorestframework-api-key
```

3. Run migrations again:

```bash
python manage.py migrate rest_framework_api_key
```

### Added

- **BREAKING**: New API key generation and validation scheme. Clients must now authorize using a single API key header. The header is `Authorization` by default. It can be customized using the `API_KEY_CUSTOM_HEADER` setting. Use the `name` field to identify clients.
- Official support for Django 2.2.
- Programmatic API key creation using `APIKey.objects.create_key()`.

### Changed

- Improved API key storage using Django's password hashing helpers. (Uses the default Django password hasher.)

### Removed

- **BREAKING**: The `HasAPIKeyOrIsAuthenticated` permission class has been removed. Please use bitwise composition now: `HasAPIKey | IsAuthenticated` (or `HasAPIKey & IsAuthenticated` for the _AND_ equivalent).
- **BREAKING**: the `DRF_API_KEY_*` settings have been removed.

## [0.4.0]

Released: 2019-04-21

### Fixed

- `HasAPIKey` now implements `.has_object_permissions()`, which allows to compose it with other permission classes and perform object-level permission checks.

### Removed

- Drop support for Python 3.4. Only 3.5, 3.6 and 3.7 are supported now.
- Drop support for Django < 2.0. Only 2.0 and 2.1 are supported now.

## [0.3.1]

Released: 2018-11-17

### Added

- `APIKey` model.
- `HasAPIKey` and `HasAPIKeyOrIsAuthenticated` permission classes.
- Generate, view and revoke API keys from the Django admin.
- Authenticate requests using the `Api-Token` and `Api-Secret-Key` headers. Customizable via the `DRF_API_KEY_TOKEN_HEADER` and `DRF_API_KEY_SECRET_KEY_HEADER` settings.

[unreleased]: https://github.com/florimondmanca/djangorestframework-api-key/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/florimondmanca/djangorestframework-api-key/compare/v0.4.0...v1.0.0
[0.4.0]: https://github.com/florimondmanca/djangorestframework-api-key/compare/v0.3.1...v0.4.0
[0.3.1]: https://github.com/florimondmanca/djangorestframework-api-key/compare/9980141e10b1dfeaaca3a6e0deebd36f5c144e7a...v0.3.1
