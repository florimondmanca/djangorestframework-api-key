# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/). This project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## 3.1.0 - 2025-04-04

### Added

- Add official support for Python 3.12 and 3.13, and Django 5.0 up to 5.2, accomodating changes to `USE_TZ`. (Pull #266)

## 3.0.0 - 2023-09-30

### Changed

- Use faster SHA512-based key hasher instead of password hashers. Reduces server load by making API key validation orders of magnitude faster (10x to 30x according to estimations, network latency aside). Hashed key will be transparently upgraded the first time `.is_valid()` is called. (Pull #244, Pull #251)

### Removed

- Dropped support for Python 3.7, which has reached EOL. (Pull #247)
- Drop redundant `.has_object_permission()` implementation on `BaseHasAPIKey` when using DRF 3.14.0 or above. (Pull #240)

### Added

- Add official support for Python 3.11. (Pull #247)

## 2.3.0 - 2023-01-19

### Removed

- Drop support for Python 3.6, which has reached EOL. (Pull #210)

### Fixed

- Fix migration 0004 when run against a non default database. (Pull #215)

## 2.2.0 - 2022-03-11

### Added

- Added support for Django config detection for different versions (PR #187)

### Changed

- Add official support for Django 3.2 and Python 3.9 and 3.10 (PR #189)
- Bumped `hashed_key` field's `max_length` from 100 to 150 to address length issue with `argon2-cffi` (PR #193)

## 2.1.0 - 2021-09-24

### Added

- Add support for custom API `keyword`. (Pull #175)

## 2.0.0 - 2020-04-07

**NOTE**: this release drops compatibility with certain Python and Django versions, but contains no other breaking changes. See [Upgrade to 2.0](https://florimondmanca.github.io/djangorestframework-api-key/upgrade/2.0/) for detailed migration steps.

### Removed

- Dropped support for Django 2.0 and Django 2.1. (Pull #126)
- Dropped support for Python 3.5. (Pull #84)

### Added

- Add support for Django 3.0. (Pull #82)
- Add support for Python 3.8. (Pull #81)
- Add `BaseAPIKeyManager.get_from_key()` to allow retrieving API keys from views. (Pull #93)
- Add type annotations, and partial support for `django-stubs` and `djangorestframework-stubs`. (Pull #88, Pull #122)

## 1.4.1 - 2019-08-24

### Added

- Now ships with type annotations ([PEP 561](https://www.python.org/dev/peps/pep-0561/)). (Pull #73)

## 1.4.0 - 2019-07-16

**NOTE**: this release contains migrations. See [Upgrade to v1.4](https://florimondmanca.github.io/djangorestframework-api-key/upgrade/1.4/) for detailed instructions.

### Added

- The `prefix` and `hashed_key` are now stored in dedicated fields on the `APIKey` model. (Pull #62)

## 1.3.0 - 2019-06-28

**NOTE**: this release contains migrations. In your Django project, run them using:

```python
python manage.py migrate rest_framework_api_key
```

### Added

- Add abstract API key model (`AbstractAPIKey`) and base manager (`BaseAPIKeyManager`). (Pull #36)
- Add base permissions (`BaseHasAPIKey`). (Pull #46)

### Changed

- The `id` field of `APIKey` is now non-`editable`.
- `APIKeyModelAdmin` does not define `fieldsets` anymore. This allows subclasses to benefit from Django's automatic fieldsets. (Pull #52)

### Fixed

- Explicitly use `utf-8` encoding in `setup.py`, which could previously lead to issues when installing on certain systems. (Pull #58)

## 1.2.1 - 2019-06-03

### Fixed

- Fixed a critical bug in `APIKeyModelAdmin` that prevented `rest_framework_api_key` from passing Django system checks. (Pull #39)

## 1.2.0 - 2019-05-29

**NOTE**: this release contains migrations. In your Django project, run them using:

```python
python manage.py migrate rest_framework_api_key
```

### Added

- API keys can now have an optional `expiry_date`. (Pull #33) `HasAPIKey` denies access if the API key has expired, i.e. if `expiry_date`, if set, is in the past.
- It is now possible to search by `prefix` in the API key admin panel.
- The `prefix` is now displayed in the edit view of the API key admin panel.

## 1.1.0 - 2019-05-14

### Added

- Improve documentation on which password hasher is used.
- Add tests against the Argon2, BcryptSHA256 and PBKDF2SHA1 hashers. (Pull #32)

### Fixed

- Fix support for password hashers that generate hashes that contain dots. (Pull #31)

## 1.0.0 - 2019-04-24

**This release is incompatible with 0.x**. See [Upgrade to 1.0](https://florimondmanca.github.io/djangorestframework-api-key/upgrade/1.4/) for migration steps.

### Removed

- Remove `HasAPIKeyOrIsAuthenticated` permission class. You should use bitwise composition now, e.g. `HasAPIKey | IsAuthenticated`.
- Drop the `DRF_API_KEY_*` settings. (Pull #19)

### Changed

- Switch to a new API key generation and validation scheme. Clients must now authorize using a single API key header (Pull #19). The header is `Authorization` by default. It can be customized using the `API_KEY_CUSTOM_HEADER` setting (Pull #26). Use the `name` field to identify clients.

### Added

- Add support for Django 2.2. (Pull #27)
- Add programmatic API key creation using `APIKey.objects.create_key()`. (Pull #19)

### Fixed

- Improved API key storage using Django's password hashing helpers. (Uses the default Django password hasher.) (Pull #19)

## 0.4.0 - 2019-04-21

### Removed

- Drop support for Python 3.4. Only 3.5, 3.6 and 3.7 are supported now.
- Drop support for Django < 2.0. Only 2.0 and 2.1 are supported now.

### Fixed

- `HasAPIKey` now implements `.has_object_permissions()`, which allows to compose it with other permission classes and perform object-level permission checks. (Pull #25)

## 0.3.1 - 2018-11-17

_Initial changelog entry._

### Added

- `APIKey` model.
- `HasAPIKey` and `HasAPIKeyOrIsAuthenticated` permission classes.
- Generate, view and revoke API keys from the Django admin.
- Authenticate requests using the `Api-Token` and `Api-Secret-Key` headers. Customizable via the `DRF_API_KEY_TOKEN_HEADER` and `DRF_API_KEY_SECRET_KEY_HEADER` settings.
