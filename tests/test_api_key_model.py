import pytest
from django.core.exceptions import ValidationError


pytestmark = pytest.mark.django_db


def test_token_generated_when_created(create_api_key):
    key = create_api_key()
    assert key.token
    assert len(key.token) >= 16
    assert key.hashed_token


def test_cannot_unrevoke(create_api_key):
    key = create_api_key(revoked=True)
    key.revoked = False
    with pytest.raises(ValidationError):
        key.save()
    with pytest.raises(ValidationError):
        key.clean()
