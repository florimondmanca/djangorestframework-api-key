"""Test the APIKey model."""

import pytest
from django.core.exceptions import ValidationError

from rest_framework_api_key.models import APIKey

pytestmark = pytest.mark.django_db


def test_encoded_value_generated_when_created():
    api_key = APIKey.objects.create(name="test")
    assert api_key.encoded


def test_cannot_unrevoke():
    api_key = APIKey.objects.create(name="test", revoked=True)
    api_key.revoked = False
    with pytest.raises(ValidationError):
        api_key.save()
    with pytest.raises(ValidationError):
        api_key.clean()
