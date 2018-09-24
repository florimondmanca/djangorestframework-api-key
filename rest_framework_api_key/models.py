"""API key models."""

from django.core.exceptions import ValidationError
from django.db import models

from .crypto import assign_token


class APIKeyManager(models.Manager):
    """Custom model manager for API keys."""

    def create(self, *, secret_key=None, **kwargs):
        """Create an API key.

        Assigns a token generated from the given secret key (or a new one).
        """
        assign_token(kwargs, secret_key=secret_key)
        return super().create(**kwargs)


class APIKey(models.Model):
    """Represents an API key."""

    objects = APIKeyManager()

    created = models.DateTimeField(auto_now_add=True)
    client_id = models.CharField(
        max_length=50, unique=True,
        help_text=(
            'A free-form unique identifier of the client. '
            '50 characters max.'
        ))
    token = models.CharField(
        max_length=40, unique=True,
        help_text=(
            'A public, unique identifier for this API key.'
        )
    )
    hashed_token = models.CharField(
        max_length=100, null=True,
        help_text=(
            'A public hash of the token, generated using the secret key '
            '(which is given to the client and not kept in database).'
        )
    )
    revoked = models.BooleanField(blank=True, default=False)

    class Meta:  # noqa
        ordering = ('-created',)
        verbose_name = 'API key'
        verbose_name_plural = 'API keys'

    def __init__(self, *args, **kwargs):
        """Store the initial value of `revoked` to detect changes."""
        super().__init__(*args, **kwargs)
        self._initial_revoked = self.revoked

    def _validated_not_unrevoked(self):
        """Validate the key has not been unrevoked."""
        if self._initial_revoked and not self.revoked:
            raise ValidationError(
                'The API key has been revoked, which cannot be undone.')

    def clean(self, *args, **kwargs):
        """Prevent from un-revoking API keys on clean."""
        super().clean(*args, **kwargs)
        self._validated_not_unrevoked()

    def save(self, *args, **kwargs):
        """Prevent from un-revoking API keys on save."""
        self._validated_not_unrevoked()
        super().save(*args, **kwargs)

    def __str__(self):
        """Represent by the client ID."""
        return str(self.client_id)
