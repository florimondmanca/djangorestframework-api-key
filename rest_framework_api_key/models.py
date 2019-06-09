from typing import Tuple
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from ._helpers import check_key, generate_key


class APIKeyManager(models.Manager):
    def create_key(self, **kwargs) -> Tuple["APIKey", str]:
        # Prevent from manually setting the primary key.
        kwargs.pop("id", None)

        obj = self.model(**kwargs)  # type: APIKey

        generated_key, prefix, hashed_key = generate_key()
        obj.prefix = prefix
        obj.hashed_key = hashed_key
        obj.save()

        return obj, generated_key

    def is_valid(self, key: str) -> bool:
        prefix, _, _ = key.partition(".")

        try:
            api_key = self.get(prefix=prefix, revoked=False)
        except self.model.DoesNotExist:
            return False

        if not api_key.is_valid(key):
            return False

        if api_key.has_expired:
            return False

        return True


class APIKey(models.Model):
    objects = APIKeyManager()

    prefix = models.CharField(max_length=8, unique=True)
    hashed_key = models.CharField(max_length=32)

    created = models.DateTimeField(auto_now_add=True, db_index=True)
    name = models.CharField(
        max_length=50,
        blank=False,
        default=None,
        help_text=(
            "A free-form name for the API key. "
            "Need not be unique. "
            "50 characters max."
        ),
    )
    revoked = models.BooleanField(
        blank=True,
        default=False,
        help_text=(
            "If the API key is revoked, clients cannot use it anymore. "
            "(This cannot be undone.)"
        ),
    )
    expiry_date = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name="Expires",
        help_text="Once API key expires, clients cannot use it anymore.",
    )

    class Meta:  # noqa
        ordering = ("-created",)
        verbose_name = "API key"
        verbose_name_plural = "API keys"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Store the initial value of `revoked` to detect changes.
        self._initial_revoked = self.revoked

    def _has_expired(self) -> bool:
        if self.expiry_date is None:
            return False
        return self.expiry_date < timezone.now()

    _has_expired.short_description = "Has expired"
    _has_expired.boolean = True
    has_expired = property(_has_expired)

    def is_valid(self, key: str) -> bool:
        return check_key(key, str(self.hashed_key))

    def clean(self):
        self._validate_revoked()

    def save(self, *args, **kwargs):
        self._validate_revoked()
        super().save(*args, **kwargs)

    def _validate_revoked(self):
        if self._initial_revoked and not self.revoked:
            raise ValidationError(
                "The API key has been revoked, which cannot be undone."
            )

    def __str__(self) -> str:
        return str(self.name)
