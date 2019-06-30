from django.apps import apps
from django.core import checks
from django.core.management import call_command

from .project.events.models import (
    Event,
    CODE_TOO_LONG,
    NAME_TOO_LONG,
    CLASHING_CODE,
    DUPLICATE_CODE,
)


def test_system_checks_pass():
    call_command("check", "rest_framework_api_key")
    call_command("check", "heroes")


def test_scope_checks():
    errors = checks.run_checks(app_configs=apps.get_app_configs())
    expected_errors = [
        checks.Error(
            "The verbose_name of model 'events.Event' "
            "must be at most 52 characters "
            "for its builtin scope names to be at most 64 characters.",
            obj=Event,
            id="rest_framework_api_key.E001",
        ),
        checks.Error(
            "The scope code '{}' of model 'events.Event' "
            "is longer than 64 characters.".format(CODE_TOO_LONG),
            obj=Event,
            id="rest_framework_api_key.E002",
        ),
        checks.Error(
            "The scope name '{}' of model 'events.Event' "
            "is longer than 64 characters.".format(NAME_TOO_LONG),
            obj=Event,
            id="rest_framework_api_key.E003",
        ),
        checks.Error(
            (
                "The scope code '{}' is duplicated for model 'events.Event'."
            ).format(DUPLICATE_CODE),
            obj=Event,
            id="rest_framework_api_key.E004",
        ),
        checks.Error(
            "The scope code '{}' clashes with a builtin scope "
            "for model 'events.Event'.".format(CLASHING_CODE),
            obj=Event,
            id="rest_framework_api_key.E005",
        ),
    ]
    assert errors == expected_errors
