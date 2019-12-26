import typing

from django.contrib import admin, messages

from .models import APIKey


class APIKeyModelAdmin(admin.ModelAdmin):
    list_display = (
        "prefix",
        "name",
        "created",
        "expiry_date",
        "_has_expired",
        "revoked",
    )
    list_filter = ("created",)
    search_fields = ("name", "prefix")

    def get_readonly_fields(
        self, request, obj: APIKey = None
    ) -> typing.Tuple[str, ...]:
        fields = ("prefix",)  # type: typing.Tuple[str, ...]
        if obj is not None and obj.revoked:
            fields = fields + ("name", "revoked", "expiry_date")
        return fields

    def save_model(self, request, obj: APIKey, form=None, change: bool = False):
        created = not obj.pk

        if created:
            key = self.model.objects.assign_key(obj)
            obj.save()
            message = (
                "The API key for {} is: {}. ".format(obj.name, key)
                + "Please store it somewhere safe: "
                + "you will not be able to see it again."
            )
            messages.add_message(request, messages.WARNING, message)
        else:
            obj.save()


admin.site.register(APIKey, APIKeyModelAdmin)

APIKeyAdmin = APIKeyModelAdmin  # Compatibility with <1.3
