import pytest
from django.contrib.contenttypes.models import ContentType
from rest_framework_api_key.models import Scope


@pytest.fixture
def hero_read() -> Scope:
    ct = ContentType.objects.get(app_label="heroes", model="hero")
    scope = Scope.objects.create(content_type=ct, code="read")
    return scope
