import pytest
from django.contrib.contenttypes.models import ContentType
from rest_framework_api_key.models import Scope


@pytest.fixture(name="hero_content_type")
def fixture_hero_content_type():
    return ContentType.objects.get(app_label="heroes", model="hero")


@pytest.fixture
def hero_read(hero_content_type) -> Scope:
    return Scope.objects.get(content_type=hero_content_type, code="read")
