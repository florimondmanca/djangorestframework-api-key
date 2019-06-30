import typing

from django.conf import settings

ScopeDeclaration = typing.Tuple[str, str]

DEFAULT_ACTIONS = ("read", "create", "update", "delete")


def get_all_scopes(opts: typing.Any) -> typing.List[ScopeDeclaration]:
    return [*get_builtin_scopes(opts), *get_custom_scopes(opts)]


def get_builtin_scopes(opts: typing.Any) -> typing.List[ScopeDeclaration]:
    return [
        (action, "Can {} {}".format(action, opts.verbose_name_raw))
        for action in DEFAULT_ACTIONS
    ]


def get_custom_scopes(opts: typing.Any) -> typing.Tuple[ScopeDeclaration]:
    scopes = getattr(settings, "API_KEY_CUSTOM_SCOPES", {})
    app_scopes = scopes.get(opts.app_label, {})
    model_scopes = app_scopes.get(opts.model_name, [])
    return model_scopes
