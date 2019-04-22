from rest_framework import permissions

from .models import APIKey


class HasAPIKey(permissions.BasePermission):
    def has_permission(self, request, view) -> bool:
        authorization = request.META.get(
            "Authorization", request.META.get("HTTP_AUTHORIZATION")
        )

        if authorization is None:
            return False

        _, _, key = authorization.partition("Api-Key ")

        return APIKey.objects.is_valid(key)

    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view)
