"""API key models."""

from typing import Tuple

from django.core.exceptions import ValidationError
from django.db import models

from .helpers import create_secret_key


class APIKeyManager(models.Manager):
    def create_key(self, **kwargs) -> Tuple["APIKey", str]:
        """Create and return an API key along with the generated secret key."""
        secret_key, encoded = create_secret_key()
        kwargs["encoded"] = encoded
        api_key = self.create(**kwargs)
        return api_key, secret_key


class APIKey(models.Model):
    """Represents an API key."""

    objects = APIKeyManager()

    created = models.DateTimeField(auto_now_add=True)
    name = models.CharField(
        max_length=50,
        unique=True,
        default=None,
        help_text=(
            "A free-form but unique name that identifies the API key owner."
        ),
    )
    encoded = models.CharField(max_length=100, unique=True, default=None)
    revoked = models.BooleanField(
        blank=True,
        default=False,
        help_text="If the API key is revoked, clients cannot use it anymore.",
    )

    class Meta:  # noqa
        ordering = ("-created",)
        verbose_name = "API key"
        verbose_name_plural = "API keys"

    def __init__(self, *args, **kwargs):
        """Store the initial value of `revoked` to detect changes."""
        super().__init__(*args, **kwargs)
        self._initial_revoked = self.revoked

    def _check_for_unrevoke(self):
        if self._initial_revoked and not self.revoked:
            raise ValidationError(
                "The API key has been revoked, which cannot be undone."
            )

    def clean(self):
        self._check_for_unrevoke()

    def save(self, *args, **kwargs):
        # Prevent from un-revoking API keys on save.
        self._check_for_unrevoke()
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return str(self.name)
