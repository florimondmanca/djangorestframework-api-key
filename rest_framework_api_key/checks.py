import typing
from itertools import chain

from django.apps import apps
from django.apps.registry import Apps
from django.core import checks
from django.db.models import Model

from .scopes import get_builtin_scopes, get_custom_scopes

ScopeDict = typing.Dict[str, str]
ErrorList = typing.List[checks.Error]


ERROR_BUILTIN_SCOPE_NAME_TOO_LONG = "rest_framework_api_key.E001"
ERROR_SCOPE_CODE_TOO_LONG = "rest_framework_api_key.E002"
ERROR_SCOPE_NAME_TOO_LONG = "rest_framework_api_key.E003"
ERROR_DUPLICATED_SCOPE = "rest_framework_api_key.E004"
ERROR_BUILTIN_SCOPE_CLASH = "rest_framework_api_key.E005"


class ModelScopeCheck:
    def __init__(
        self, model: Model, name_max_length: str, code_max_length: str
    ):
        self.model = model
        self.name_max_length = name_max_length
        self.code_max_length = code_max_length
        self.opts = getattr(self.model, "_meta")  # type: typing.Any
        self.model_name = "{}.{}".format(
            self.opts.app_label, self.opts.object_name
        )
        self.builtin_scopes = dict(
            get_builtin_scopes(self.opts)
        )  # type: ScopeDict
        self.codes = set()
        self.errors = None  # type: ErrorList

    def _add_error(self, message: str, iden: str):
        self.errors.append(checks.Error(message, obj=self.model, id=iden))

    def _check_builtin_scope_name_lengths(self):
        max_builtin_scope_name_length = max(
            (len(name) for name in self.builtin_scopes.values()), default=0
        )

        if max_builtin_scope_name_length > self.name_max_length:
            verbose_name_max_length = self.name_max_length - (
                max_builtin_scope_name_length - len(self.opts.verbose_name_raw)
            )
            self._add_error(
                (
                    "The verbose_name of model '{}' "
                    "must be at most {} characters "
                    "for its builtin scope names to be at most {} characters."
                ).format(
                    self.model_name,
                    verbose_name_max_length,
                    self.name_max_length,
                ),
                iden=ERROR_BUILTIN_SCOPE_NAME_TOO_LONG,
            )

    def _check_name_length(self, name: str):
        if len(name) > self.name_max_length:
            self._add_error(
                (
                    "The scope name '{}' of model '{}' "
                    "is longer than {} characters."
                ).format(name, self.model_name, self.name_max_length),
                iden=ERROR_SCOPE_NAME_TOO_LONG,
            )

    def _check_code_length(self, code: str):
        if len(code) > self.code_max_length:
            self._add_error(
                (
                    "The scope code '{}' of model '{}' "
                    "is longer than {} characters."
                ).format(code, self.model_name, self.code_max_length),
                iden=ERROR_SCOPE_CODE_TOO_LONG,
            )

    def _check_builtin_scope_clash(self, code: str) -> bool:
        if code in self.builtin_scopes:
            self._add_error(
                (
                    "The scope code '{}' clashes with a builtin scope "
                    "for model '{}'."
                ).format(code, self.model_name),
                iden=ERROR_BUILTIN_SCOPE_CLASH,
            )
            return True
        return False

    def _check_duplicated_scope(self, code: str):
        if code in self.codes:
            self._add_error(
                "The scope code '{}' is duplicated for model '{}'.".format(
                    code, self.model_name
                ),
                iden=ERROR_DUPLICATED_SCOPE,
            )

    def __call__(self, errors: ErrorList) -> None:
        self.errors = errors
        self._check_builtin_scope_name_lengths()

        for code, name in get_custom_scopes(self.opts):
            self._check_name_length(name)
            self._check_code_length(code)
            clashes = self._check_builtin_scope_clash(code)
            if not clashes:
                self._check_duplicated_scope(code)
            self.codes.add(code)


def _get_max_length(model: Model, field: str) -> int:
    return getattr(model, "_meta").get_field(field).max_length


def check_models_scopes(app_configs: Apps = None, **_: typing.Any) -> ErrorList:
    if app_configs is None:
        models = apps.get_models()
    else:
        models = chain.from_iterable(
            app_config.get_models() for app_config in app_configs
        )

    scope_model = apps.get_model("rest_framework_api_key", "Scope")
    errors = []  # type: ErrorList

    for model in models:
        ModelScopeCheck(
            model,
            name_max_length=_get_max_length(scope_model, "name"),
            code_max_length=_get_max_length(scope_model, "code"),
        )(errors)

    return errors
