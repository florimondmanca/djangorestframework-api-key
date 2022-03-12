# Contributing

Thanks for your interest in contributing to this project!

Here are a few ways in which you can help:

- Discovered a bug? Please open a [bug report](https://github.com/florimondmanca/djangorestframework-api-key/issues/new?template=bug_report.md).
- Have a feature you'd like to see implemented? Please open a [Feature Request](https://github.com/florimondmanca/djangorestframework-api-key/issues/new?template=feature_request.md).
- For any other contribution, please open a [discussion](https://github.com/florimondmanca/djangorestframework-api-key/issues/new?template=discussion.md).

**NOTE**: for **non-trivial changes** we _highly_ encourage you to **open an issue** first. This will allow maintainers and contributors to confirm that the problem you are trying to solve is well-posed, in the scope of the project, and/or can't be solved with existing features.

### Installation

1. Fork the repository.
1. Clone it on your machine.
1. Install dependencies:

```
make install
```

### Tests

Run the tests using:

```
make test
```

### Code style

Run code auto-formatting with:

```
make format
```

Run code style checks using:

```
make check
```

### Generating migrations

This package includes migrations. To update them in case of changes without setting up a Django project, run:

```
make migrations
```

### Documentation

Build the documentation using:

```
make docs
```

Serve the docs site locally (with hot-reload) using:

```
make docs-serve
```

## Notes to maintainers

### Releasing

- Create a release PR with the following:
  - Bump the package version by editing `__version__.py`.
  - Update the changelog with any relevant PRs merged since the last version: bug fixes, new features, changes, deprecations, removals.
- Once the release PR is merged, create a [new release](https://github.com/florimondmanca/djangorestframework-api-key/releases/new), including:
    - Tag version, like `2.1.0`.
    - Release title, `Version 2.1.0`.
    - Description copied from the changelog.
- Once created, this release will be automatically uploaded to PyPI via a publish job on Azure Pipelines.
- Deploy the docs using: `make docs-deploy`
