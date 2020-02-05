import typing

from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import BasePermission


def create_view_with_permissions(
    *classes: typing.Type[BasePermission],
) -> typing.Callable:
    @api_view()
    @permission_classes(classes)
    def view(*args: typing.Any) -> Response:
        return Response()

    return view
