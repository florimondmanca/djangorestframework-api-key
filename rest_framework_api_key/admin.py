import typing

from django.contrib import admin, messages

from ._helpers import generate_key
from .models import APIKey


class APIKeyAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "prefix",
        "created",
        "expiry_date",
        "_has_expired",
        "revoked",
    )
    list_filter = ("created",)
    search_fields = ("name", "prefix")
    fieldsets = (
        (None, {"fields": ("name", "prefix", "expiry_date", "revoked")}),
    )

    def get_readonly_fields(
        self, request, obj: APIKey = None
    ) -> typing.Tuple[str]:
        fields = ("prefix",)
        if obj is not None and obj.revoked:
            fields = fields + ("name", "revoked", "expiry_date")
        return fields

    def get_api_key(self, obj: APIKey) -> str:
        if obj.pk:
            return 16 * "*"
        return "The API key will be generated when clicking 'Save'."

    get_api_key.short_description = "API key"

    def save_model(self, request, obj: APIKey, form, change):
        created = not obj.pk

        if created:
            generated_key, key_id = generate_key()
            obj.id = key_id

            obj.save()

            message = (
                "The API key for {} is: {}. ".format(obj.name, generated_key)
                + "Please store it somewhere safe: "
                + "you will not be able to see it again."
            )
            messages.add_message(request, messages.WARNING, message)
        else:
            obj.save()


admin.site.register(APIKey, APIKeyAdmin)
