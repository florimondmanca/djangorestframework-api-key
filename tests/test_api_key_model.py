"""Test the APIKey model."""

import pytest
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from django.utils.crypto import get_random_string

from rest_framework_api_key.models import APIKey

pytestmark = pytest.mark.django_db


def test_encoded_value_generated_when_created():
    api_key, secret_key = APIKey.objects.create_key(name="test")
    assert secret_key is not None
    assert api_key.encoded


@pytest.mark.parametrize("field", ("name", "encoded"))
def test_required_fields(field):
    kwargs = {"name": "test", "encoded": "abcd"}
    kwargs.pop(field)
    with pytest.raises(IntegrityError):
        APIKey.objects.create(**kwargs)


@pytest.mark.parametrize("field", ("name", "encoded"))
def test_unique_fields(field):
    kwargs = {"name": get_random_string(), "encoded": get_random_string()}
    value = kwargs[field]
    APIKey.objects.create(**kwargs)

    kwargs = {"name": get_random_string(), "encoded": get_random_string()}
    kwargs[field] = value
    with pytest.raises(IntegrityError):
        APIKey.objects.create(**kwargs)


def test_cannot_unrevoke():
    api_key, _ = APIKey.objects.create_key(name="test", revoked=True)
    api_key.revoked = False
    with pytest.raises(ValidationError):
        api_key.save()
    with pytest.raises(ValidationError):
        api_key.clean()
