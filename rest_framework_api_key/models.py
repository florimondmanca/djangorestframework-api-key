"""API key models."""

from django.core.exceptions import ValidationError
from django.db import models

from .utils import generate_key


class APIKey(models.Model):
    """Represents an API key."""

    created = models.DateTimeField(auto_now_add=True)
    client_id = models.CharField(
        max_length=50, unique=True,
        help_text=(
            'A free-form unique identifier of the client. '
            '50 characters max.'
        ))
    key = models.CharField(max_length=40, unique=True)
    revoked = models.BooleanField(blank=True, default=False)

    class Meta:  # noqa
        ordering = ('-created',)
        verbose_name = 'API key'
        verbose_name_plural = 'API keys'

    def __init__(self, *args, **kwargs):
        """Store the initial value of `revoked` to detect changes."""
        super().__init__(*args, **kwargs)
        self.initial_revoked = self.revoked

    def _validated_not_unrevoked(self):
        """Validate the key has not been unrevoked."""
        if self.initial_revoked and not self.revoked:
            raise ValidationError(
                'The API key has been revoked, which cannot be undone.')

    def clean(self, *args, **kwargs):
        """Customize instance cleaning."""
        super().clean(*args, **kwargs)
        self._validated_not_unrevoked()

    def save(self, *args, **kwargs):
        """Customize instance saving.

        Generate a key on model instance creation.
        Prevent from un-revoking API keys.
        """
        if not self.pk:
            self.key = generate_key()
        self._validated_not_unrevoked()
        super().save(*args, **kwargs)

    def __str__(self):
        """Represent by the client ID."""
        return str(self.client_id)
