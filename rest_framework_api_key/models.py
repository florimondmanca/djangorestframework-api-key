"""API key models."""

from django.core.exceptions import ValidationError
from django.core.validators import validate_slug
from django.db import models

from .helpers import create_secret_key


class APIKeyManager(models.Manager):
    """Custom model manager for API keys."""

    def create(self, **kwargs) -> "APIKey":
        """Create an API key.

        Assigns a token generated from the given secret key (or a new one).
        """
        if "encoded" not in kwargs:
            _, encoded = create_secret_key()
            kwargs["encoded"] = encoded
        return super().create(**kwargs)


class APIKey(models.Model):
    """Represents an API key."""

    objects = APIKeyManager()

    created = models.DateTimeField(auto_now_add=True)
    name = models.CharField(
        max_length=50,
        unique=True,
        help_text=(
            "A unique snake-cased name of the client. " "50 characters max."
        ),
        validators=[validate_slug],
    )
    encoded = models.CharField(max_length=100, null=True)
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
