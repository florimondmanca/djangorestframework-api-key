from typing import Any, Tuple

import pytest

try:
    from django_test_migrations.migrator import Migrator
except ImportError:  # pragma: no cover
    # Most likely Django < 3.2
    Migrator = None  # type: ignore

pytestmark = pytest.mark.skipif(
    Migrator is None,
    reason="django-test-migrations is not available",
)


@pytest.mark.django_db
def test_migrations_0001_initial(migrator: Migrator) -> None:
    old_state = migrator.apply_initial_migration(("rest_framework_api_key", None))

    with pytest.raises(LookupError):
        old_state.apps.get_model("rest_framework_api_key", "APIKey")

    new_state = migrator.apply_tested_migration(
        ("rest_framework_api_key", "0001_initial")
    )
    APIKey = new_state.apps.get_model("rest_framework_api_key", "APIKey")
    assert APIKey.objects.count() == 0


@pytest.mark.django_db
def test_migrations_0004_prefix_hashed_key(migrator: Migrator) -> None:
    from django.contrib.auth.hashers import make_password
    from django.utils.crypto import get_random_string

    def _generate() -> Tuple[str, str]:
        # Replicate bejavior before PR #62 (i.e. before v1.4).
        prefix = get_random_string(8)
        secret_key = get_random_string(32)
        key = prefix + "." + secret_key
        key_id = prefix + "." + make_password(key)
        return key, key_id

    def _assign_key(obj: Any) -> None:
        # Replicate bejavior before PR #62 (i.e. before v1.4).
        _, hashed_key = _generate()
        pk = hashed_key
        prefix, _, hashed_key = hashed_key.partition(".")

        obj.id = pk
        obj.prefix = prefix
        obj.hashed_key = hashed_key

    old_state = migrator.apply_initial_migration(
        ("rest_framework_api_key", "0003_auto_20190623_1952")
    )

    APIKey = old_state.apps.get_model("rest_framework_api_key", "APIKey")

    # Create a key as it if were created before PR #62 (i.e. before v1.4).
    api_key = APIKey.objects.create(name="test")
    _assign_key(api_key)
    api_key.save()
    prefix, _, hashed_key = api_key.id.partition(".")

    # Apply migration added by PR #62.
    new_state = migrator.apply_tested_migration(
        ("rest_framework_api_key", "0004_prefix_hashed_key")
    )
    APIKey = new_state.apps.get_model("rest_framework_api_key", "APIKey")

    # Ensure new `prefix`` and `hashed_key` fields were successfully populated.
    api_key = APIKey.objects.get(id=api_key.id)
    assert api_key.prefix == prefix
    assert api_key.hashed_key == hashed_key
