"""rest_framework_api_key administration panel."""

from django.contrib import admin, messages
from .models import APIKey
from .crypto import assign_token


_SECRET = 16 * '*'
_SECRET_KEY_MESSAGE = (
    'The secret key for {client_id} is: {secret_key}. '
    'Please note it down: you will not be able to see it again.'
)


@admin.register(APIKey)
class APIKeyAdmin(admin.ModelAdmin):
    """Admin panel for API keys."""

    list_display = ('client_id', 'created', 'revoked')
    list_filter = ('created', 'revoked',)
    readonly_fields = ('token', 'secret_key_message')
    search_fields = ('id', 'client_id',)
    fieldsets = (
        (None, {
            'fields': ('client_id', 'revoked',),
        }),
        ('Credentials', {
            'fields': ('token', 'secret_key_message',),
        }),
    )

    def get_readonly_fields(self, request, obj=None):
        """Set revoked as read-only if the API key has been revoked."""
        if obj and obj.revoked:
            return self.readonly_fields + ('client_id', 'revoked',)
        return self.readonly_fields

    def secret_key_message(self, obj):
        """Show a message about the secret key."""
        if obj.pk:
            return _SECRET
        return 'The secret key will be generated when clicking save.'
    secret_key_message.short_description = 'Secret key'

    def save_model(self, request, obj, form, change):
        """Display the API key on save."""
        if not obj.pk:
            # If the object is being created, generate its token.
            secret_key = assign_token(obj)
            obj.save()
            message = _SECRET_KEY_MESSAGE.format(
                client_id=obj.client_id,
                secret_key=secret_key,
            )
            messages.add_message(request, messages.WARNING, message)
        else:
            # Save as usual
            obj.save()
