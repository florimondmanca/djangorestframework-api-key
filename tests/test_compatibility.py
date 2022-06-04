import django
import pytest

import rest_framework_api_key


@pytest.mark.skipif(
    django.VERSION < (3, 2), reason="app config is automatically defined by django"
)
def test_app_config_not_defined() -> None:  # pragma: no cover
    assert hasattr(rest_framework_api_key, "default_app_config") is False


@pytest.mark.skipif(
    django.VERSION >= (3, 2), reason="app config is not automatically defined by django"
)
def test_app_config_defined() -> None:  # pragma: no cover
    assert hasattr(rest_framework_api_key, "default_app_config") is True
