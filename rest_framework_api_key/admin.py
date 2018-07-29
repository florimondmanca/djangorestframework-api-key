"""rest_framework_api_key administration panel."""

from django.contrib import admin, messages
from .models import APIKey


_SECRET = 16 * '*'
_API_KEY_MESSAGE = (
    'The API key for {obj.client_id} is {obj.key}. '
    'Please note it down: you will not be able to see it again.'
)


@admin.register(APIKey)
class APIKeyAdmin(admin.ModelAdmin):
    """Admin panel for API keys."""

    list_display = ('client_id', 'created', 'revoked', 'id')
    list_filter = ('created', 'revoked',)
    readonly_fields = ('key_message',)
    search_fields = ('id', 'client_id',)
    fieldsets = (
        (None, {
            'fields': ('client_id', 'key_message', 'revoked',),
        }),
    )

    def get_readonly_fields(self, request, obj=None):
        """Set revoked as read-only if API key has been revoked."""
        if obj and obj.revoked:
            return self.readonly_fields + ('client_id', 'revoked',)
        return self.readonly_fields

    def key_message(self, obj: APIKey) -> str:
        """Message displayed instead of the API key."""
        if obj.key:
            return _SECRET
        return 'The API key will be generated once you click save.'
    key_message.short_description = 'Key'

    def save_model(self, request, obj, form, change):
        """Display the API key on save."""
        if not obj.pk:
            obj.save()
            message = _API_KEY_MESSAGE.format(obj=obj)
            messages.add_message(request, messages.WARNING, message)
        else:
            obj.save()
