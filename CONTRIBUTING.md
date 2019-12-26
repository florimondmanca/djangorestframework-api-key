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

```bash
scripts/install
```

### Tests

Run the tests using:

```bash
scripts/test
```

### Code style

Run code auto-formatting with:

```bash
scripts/lint
```

Run code style checks using:

```bash
scripts/check
```

### Generating migrations

This package includes migrations. To update them in case of changes without setting up a Django project, run:

```bash
scripts/makemigrations
```

### Documentation

Serve the docs site locally (with hot-reload) using:

```bash
scripts/serve
```

Build the documentation using:

```bash
scripts/docs
```

## Notes to maintainers

### Releasing

- Create a PR with the following:
  - Bump the package version by editing `__version__.py`.
  - Update the changelog with any relevant PRs merged since the last version: bug fixes, new features, changes, deprecations, removals.
- Merge the PR.
- Run `$ scripts/publish` on `master`.
- Tag the commit and push the tag to the remote.
