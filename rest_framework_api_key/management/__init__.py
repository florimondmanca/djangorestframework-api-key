import typing

from django.apps import apps as global_apps
from django.apps.registry import Apps
from django.contrib.contenttypes.management import create_contenttypes
from django.db import DEFAULT_DB_ALIAS, router

from ..scopes import ScopeDeclaration, get_all_scopes


def create_scopes(
    app_config,
    interactive: bool = True,
    verbosity: int = 2,
    using: str = DEFAULT_DB_ALIAS,
    apps: Apps = global_apps,
    **kwargs,
):
    if not app_config.models_module:
        return

    # Ensure that contenttypes are created for this app.
    # Needed if `rest_framework_api_key` is in `INSTALLED_APPS` before
    # `django.contrib.contenttypes`.
    create_contenttypes(
        app_config,
        verbosity=verbosity,
        interactive=interactive,
        using=using,
        apps=apps,
        **kwargs,
    )

    app_label = app_config.label
    try:
        app_config = apps.get_app_config(app_label)
        ContentType = apps.get_model("contenttypes", "ContentType")
        Scope = apps.get_model("rest_framework_api_key", "Scope")
    except LookupError:
        return

    if not router.allow_migrate_model(using, Scope):
        return

    searched_scopes = (
        []
    )  # type: typing.List[typing.Tuple[ContentType, ScopeDeclaration]]

    content_types = set()
    for cls in app_config.get_models():
        # Force looking up the content types in the current database
        # before creating foreign keys to them.
        content_type = ContentType.objects.db_manager(using).get_for_model(
            cls, for_concrete_model=False
        )
        content_types.add(content_type)
        options = getattr(cls, "_meta")
        for (code, name) in get_all_scopes(options):
            searched_scopes.append((content_type, (code, name)))

    existing_scopes = set(
        Scope.objects.using(using)
        .filter(content_type__in=content_types)
        .values_list("content_type", "code")
    )  # type: typing.Set[typing.Tuple[int, str]]

    scopes = [
        Scope(code=code, name=name, content_type=ct)
        for ct, (code, name) in searched_scopes
        if (ct.pk, code) not in existing_scopes
    ]  # type: typing.List[Scope]

    Scope.objects.using(using).bulk_create(scopes)

    if verbosity >= 2:
        for scope in scopes:
            print("Adding API key scope '{}'".format(scope))
