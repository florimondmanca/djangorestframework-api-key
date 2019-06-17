import re

from django import forms


def validate_regex_pattern(pattern):
    try:
        re.compile(pattern)
        return True
    except re.error:
        raise forms.ValidationError('Invalid regex pattern')
