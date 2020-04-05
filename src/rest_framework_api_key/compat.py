import typing


def generic_meta(name: str, mcs: type) -> type:
    """
    Given a metaclass, return a metaclass that's compatible
    with subclassing from `typing.Generic` and an instance of `mcs`, eg:

    Usage:

    ```python
    >>> from typing import Any, Generic, TypeVar
    >>> T = TypeVar("T")
    >>> class MetaA(type): ...
    >>> class A(metaclass=MetaA): ...
    >>> MetaB: Any = generic_meta("MetaB", MetaA)
    >>> class B(Generic[T], A, metaclass=MetaB): ...
    ```

    This is a workaround for runtime metaclass conflicts caused by `GenericMeta`
    on Python 3.6.

    See: https://www.python.org/dev/peps/pep-0560/#metaclass-conflicts
    """
    try:
        GenericMeta = typing.GenericMeta
    except AttributeError:
        # Python 3.7+
        return mcs
    else:
        # Python 3.6
        return type(name, (GenericMeta, mcs), {})
