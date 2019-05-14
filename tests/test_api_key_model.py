import string

import pytest
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from rest_framework_api_key.models import APIKey

pytestmark = pytest.mark.django_db


def test_key_generation():
    api_key, generated_key = APIKey.objects.create_key(name="test")
    prefix, _, hashed_key = api_key.id.partition(".")

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
