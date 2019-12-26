def patch_django_models_generics() -> None:
    """
    Add a no-op '.__class_getitem__()' runtime implementation to QuerySet and Manager
    so that users can use 'QuerySet[MyModel]' and 'Manager[MyModel]' with django-stubs.

    Inspired by:
    https://github.com/typeddjango/django-stubs/blob/31e795016f154309e675c85616f4f8af033c0860/mypy_django_plugin/django/context.py#L48
    """

    def noop_class_getitem(cls: type, key: str) -> type:
        return cls

    from django.db import models

    if not hasattr(models.QuerySet, "__class_getitem__"):
        models.QuerySet.__class_getitem__ = classmethod(  # type: ignore
            noop_class_getitem
        )

    if not hasattr(models.Manager, "__class_getitem__"):
        models.Manager.__class_getitem__ = classmethod(  # type: ignore
            noop_class_getitem
        )
