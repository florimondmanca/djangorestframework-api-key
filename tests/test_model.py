import string

import pytest
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from rest_framework_api_key.models import APIKey

from .dateutils import NOW, TOMORROW, YESTERDAY
from .project.heroes.models import HeroAPIKey, Hero

pytestmark = pytest.mark.django_db


def test_key_generation():
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


def test_name_is_required():
    with pytest.raises(IntegrityError):
        APIKey.objects.create()


def test_cannot_unrevoke():
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
def test_has_expired(expiry_date, has_expired):
    api_key, _ = APIKey.objects.create_key(name="test", expiry_date=expiry_date)
    assert api_key.has_expired is has_expired


def test_custom_api_key_model():
    hero = Hero.objects.create()
    hero_api_key, generated_key = HeroAPIKey.objects.create_key(
        name="test", hero=hero
    )
    assert hero_api_key.is_valid(generated_key)
    assert hero_api_key.hero.id == hero.id
    assert hero.api_keys.first() == hero_api_key
