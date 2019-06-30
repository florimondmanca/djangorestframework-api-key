from django.apps import apps
from django.core import checks
from django.core.management import call_command
from .project.heroes.models import Hero
from .project.events.models import Event


CODE = "launch"
NAME = "Can launch a hero"
CODE_TOO_LONG = CODE * 20
NAME_TOO_LONG = NAME * 20
DUPLICATE_CODE = CODE
CLASHING_CODE = "create"


def test_system_checks_pass():
    call_command("check", "rest_framework_api_key")
    call_command("check", "heroes")


def test_scope_checks(settings):
    settings.API_KEY_CUSTOM_SCOPES["heroes"] = {
        "hero": [
            (CODE_TOO_LONG, NAME),
            (CODE, NAME_TOO_LONG),
            (DUPLICATE_CODE, NAME),
            (CLASHING_CODE, NAME),
        ]
    }

    errors = checks.run_checks(app_configs=apps.get_app_configs())
    expected_errors = [
        checks.Error(
            "The scope code '{}' of model 'heroes.Hero' "
            "is longer than 64 characters.".format(CODE_TOO_LONG),
            obj=Hero,
            id="rest_framework_api_key.E002",
        ),
        checks.Error(
            "The scope name '{}' of model 'heroes.Hero' "
            "is longer than 64 characters.".format(NAME_TOO_LONG),
            obj=Hero,
            id="rest_framework_api_key.E003",
        ),
        checks.Error(
            (
                "The scope code '{}' is duplicated for model 'heroes.Hero'."
            ).format(DUPLICATE_CODE),
            obj=Hero,
            id="rest_framework_api_key.E004",
        ),
        checks.Error(
            "The scope code '{}' clashes with a builtin scope "
            "for model 'heroes.Hero'.".format(CLASHING_CODE),
            obj=Hero,
            id="rest_framework_api_key.E005",
        ),
        checks.Error(
            "The verbose_name of model 'events.Event' "
            "must be at most 53 characters "
            "for its builtin scope names to be at most 64 characters.",
            obj=Event,
            id="rest_framework_api_key.E001",
        ),
    ]
    assert errors == expected_errors
