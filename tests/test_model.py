import datetime as dt
import string

import pytest
from django.contrib.auth.hashers import make_password
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from test_project.heroes.models import Hero, HeroAPIKey

from rest_framework_api_key.models import APIKey

from .dateutils import NOW, TOMORROW, YESTERDAY

pytestmark = pytest.mark.django_db


def test_key_generation() -> None:
    api_key, generated_key = APIKey.objects.create_key(name="test")
    prefix = api_key.prefix
    hashed_key = api_key.hashed_key

    assert prefix and hashed_key

    charset = set(string.ascii_letters + string.digits + ".")
    assert all(c in charset for c in generated_key)

    # The generated key must be valid…
    assert api_key.is_valid(generated_key) is True

    # But not the hashed key.
    assert api_key.is_valid(hashed_key) is False


def test_name_is_required() -> None:
    with pytest.raises(IntegrityError):
        APIKey.objects.create()


def test_cannot_unrevoke() -> None:
    api_key, _ = APIKey.objects.create_key(name="test", revoked=True)

    # Try to unrevoke the API key programmatically.
    api_key.revoked = False

    with pytest.raises(ValidationError):
        api_key.save()

    with pytest.raises(ValidationError):
        api_key.clean()


@pytest.mark.parametrize(
    "expiry_date, has_expired",
    [(None, False), (NOW, True), (TOMORROW, False), (YESTERDAY, True)],
)
def test_has_expired(expiry_date: dt.datetime, has_expired: bool) -> None:
    api_key, _ = APIKey.objects.create_key(name="test", expiry_date=expiry_date)
    assert api_key.has_expired is has_expired


def test_custom_api_key_model() -> None:
    hero = Hero.objects.create()
    hero_api_key, generated_key = HeroAPIKey.objects.create_key(name="test", hero=hero)
    assert hero_api_key.is_valid(generated_key)
    assert hero_api_key.hero.id == hero.id
    assert hero.api_keys.first() == hero_api_key


@pytest.mark.django_db
def test_api_key_hash_upgrade() -> None:
    """Tests the hashing algo upgrade from Django's PW hashers to sha512."""
    key_generator = APIKey.objects.key_generator

    api_key, generated_key = APIKey.objects.create_key(name="test")
    assert api_key.is_valid(generated_key)
    assert key_generator.using_preferred_hasher(api_key.hashed_key)

    # Use Django's built-in hashers, the old way of storing a key
    api_key.hashed_key = make_password(generated_key)
    api_key.save()

    # Simple sanity check to ensure the hash is still being checked
    # and that we aren't using the preferred hasher (using Django's slower hashers)
    assert not api_key.is_valid(key_generator.hash("invalid-key"))
    assert not key_generator.using_preferred_hasher(api_key.hashed_key)

    # After calling `is_valid`, the key has been upgraded to use the preferred hasher
    assert api_key.is_valid(generated_key)
    assert key_generator.using_preferred_hasher(api_key.hashed_key)


@pytest.mark.django_db
def test_api_key_manager_get_from_key() -> None:
    api_key, generated_key = APIKey.objects.create_key(name="test")
    retrieved_key = APIKey.objects.get_from_key(generated_key)
    assert retrieved_key == api_key


@pytest.mark.django_db
def test_api_key_manager_get_from_key_missing_key() -> None:
    with pytest.raises(APIKey.DoesNotExist):
        APIKey.objects.get_from_key("foobar")


@pytest.mark.django_db
def test_api_key_manager_get_from_key_invalid_key() -> None:
    api_key, generated_key = APIKey.objects.create_key(name="test")
    prefix, _, _ = generated_key.partition(".")
    invalid_key = f"{prefix}.foobar"
    with pytest.raises(APIKey.DoesNotExist):
        APIKey.objects.get_from_key(invalid_key)


def test_api_key_str() -> None:
    _, generated_key = APIKey.objects.create_key(name="test")
    retrieved_key = APIKey.objects.get_from_key(generated_key)
    assert str(retrieved_key) == "test"
