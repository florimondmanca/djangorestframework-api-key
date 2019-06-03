#!/bin/bash

# Stop if any command fails.
set -e

ARGS="$@"
CHANGELOG="CHANGELOG.md"

get () {
    bumpversion --dry-run --list $ARGS | grep $1 | sed s,"^.*=",,
}

CURRENT_VERSION=$(get current_version)
NEW_VERSION=$(get new_version)

bumpversion "$@" --no-tag --no-commit
python scripts/changelog_bump.py "$CHANGELOG" "v$NEW_VERSION"

git add -A
git commit -m "Bump version: $CURRENT_VERSION → $NEW_VERSION"
git tag "v$NEW_VERSION"
