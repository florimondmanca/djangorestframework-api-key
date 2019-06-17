import pytest
from django import forms

from rest_framework_api_key import validators


valid_data = [
    'abc',
    'abc/[a-z0-9]{4}/def',
]

invalid_data = [
    '[',
]


@pytest.mark.parametrize('pattern', valid_data)
def test_validate_regex_pattern_with_valid_data(pattern):
    assert validators.validate_regex_pattern(pattern)


@pytest.mark.parametrize('pattern', invalid_data)
def test_validate_regex_pattern_with_invalid_data(pattern):
    with pytest.raises(forms.ValidationError):
        validators.validate_regex_pattern(pattern)
