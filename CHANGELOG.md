# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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

[unreleased]: https://github.com/florimondmanca/djangorestframework-api-key/compare/v0.3.1...HEAD
[0.3.1]: https://github.com/florimondmanca/djangorestframework-api-key/compare/9980141e10b1dfeaaca3a6e0deebd36f5c144e7a...v0.3.1
