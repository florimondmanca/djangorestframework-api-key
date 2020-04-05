import typing

if typing.TYPE_CHECKING:
    from .models import AbstractAPIKey  # noqa: F401

K = typing.TypeVar("K", bound="AbstractAPIKey")
