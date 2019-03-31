"""rest_framework_api_key administration panel."""

from typing import Tuple

from django.contrib import admin, messages

from .crypto import create_secret_key
from .models import APIKey

_SECRET = 16 * "*"


@admin.register(APIKey)
class APIKeyAdmin(admin.ModelAdmin):
    """Admin panel for API keys."""

    list_display = ("name", "created", "revoked")
    list_filter = ("created", "revoked")
    readonly_fields = ("secret_key_message",)
    search_fields = ("name",)
    fieldsets = (
        (None, {"fields": ("name", "revoked")}),
        ("Credentials", {"fields": ("secret_key_message",)}),
    )

    def get_readonly_fields(self, request, obj: APIKey = None) -> Tuple[str]:
        """Set revoked as read-only if the API key has been revoked."""
        if obj is not None and obj.revoked:
            return self.readonly_fields + ("name", "revoked")
        return self.readonly_fields

    @staticmethod
    def secret_key_message(obj: APIKey) -> str:
        if obj.pk:
            return _SECRET
        return "The secret key will be generated when clicking 'Save'."

    secret_key_message.short_description = "Secret key"

    def save_model(self, request, obj: APIKey, form, change):
        """Display the API key on save."""
        created = not obj.pk

        if created:
            secret_key, encoded = create_secret_key()
            obj.encoded = encoded

        obj.save()

        if created:
            message = (
                "The secret key for {} is: {}. ".format(obj.name, secret_key)
                + "Please note it down: you will not be able to see it again."
            )
            messages.add_message(request, messages.WARNING, message)
