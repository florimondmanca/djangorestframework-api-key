import typing

from django.contrib import admin, messages
from django.utils.html import format_html_join
from django.utils.safestring import mark_safe

from .models import APIKey, APIKeyGroup, EndpointPermission


class APIKeyAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "prefix",
        "created",
        "expiry_date",
        "_has_expired",
        "revoked",
        "group",
    )
    list_filter = ("created",)
    search_fields = ("name", "prefix")
    fieldsets = (
        (None, {"fields": ("name", "prefix", "expiry_date", "revoked", "group")}),
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

    def save_model(self, request, obj: APIKey, form=None, change: bool = None):
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



class APIKeyGroupEndpointPermissionInline(admin.TabularInline):
    model = APIKeyGroup.endpoint_permissions.through
    verbose_name = 'API Key Group <-> Endpoint Permission Relationship'
    verbose_name_plural = 'API Key Group <-> Endpoint Permission Relationships'


@admin.register(APIKeyGroup)
class APIKeyGroupAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'get_endpoint_permissions',
        'get_number_of_api_keys_in_group',
    )

    def get_endpoint_permissions(self, obj):
        return format_html_join(
            mark_safe('<br>'),
            '{}',
            ((str(endpoint_permission),)
             for endpoint_permission in obj.endpoint_permissions.all()),
        )

    def get_number_of_api_keys_in_group(self, obj):
        return APIKey.objects.all().filter(group=obj).count()

    get_endpoint_permissions.short_description = 'Endpoint Permissions'
    get_number_of_api_keys_in_group.short_description = 'API Key Count'


@admin.register(EndpointPermission)
class EndpointPermissionAdmin(admin.ModelAdmin):
    inlines = [
        APIKeyGroupEndpointPermissionInline,
    ]
    list_display = (
        'path',
        'method',
    )

admin.site.register(APIKey, APIKeyAdmin)
