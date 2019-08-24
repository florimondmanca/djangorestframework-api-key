from typing import Tuple

from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from .crypto import concatenate, KeyGenerator, split


class BaseAPIKeyManager(models.Manager):
    key_generator = KeyGenerator()

    def assign_key(self, obj: "AbstractAPIKey") -> str:
        try:
            key, prefix, hashed_key = self.key_generator.generate()
        except ValueError:  # Compatibility with < 1.4
            key, hashed_key = self.key_generator.generate()  # type: ignore
            pk = hashed_key
            prefix, hashed_key = split(hashed_key)
        else:
            pk = concatenate(prefix, hashed_key)

        obj.id = pk
        obj.prefix = prefix
        obj.hashed_key = hashed_key

        return key

    def create_key(self, **kwargs) -> Tuple["AbstractAPIKey", str]:
        # Prevent from manually setting the primary key.
        kwargs.pop("id", None)
        obj = self.model(**kwargs)  # type: AbstractAPIKey
        key = self.assign_key(obj)
        obj.save()
        return obj, key

    def get_usable_keys(self) -> models.QuerySet:
        return self.filter(revoked=False)

    def is_valid(self, key: str) -> bool:
        prefix, _, _ = key.partition(".")

        queryset = self.get_usable_keys()

        try:
            api_key = queryset.get(prefix=prefix)  # type: AbstractAPIKey
        except self.model.DoesNotExist:
            return False

        if not api_key.is_valid(key):
            return False

        if api_key.has_expired:
            return False

        return True


class APIKeyManager(BaseAPIKeyManager):
    pass


class AbstractAPIKey(models.Model):
    objects = APIKeyManager()

    id = models.CharField(max_length=100, unique=True, primary_key=True, editable=False)
    prefix = models.CharField(max_length=8, unique=True, editable=False)
    hashed_key = models.CharField(max_length=100, editable=False)
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
        abstract = True
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

    _has_expired.short_description = "Has expired"  # type: ignore
    _has_expired.boolean = True  # type: ignore
    has_expired = property(_has_expired)

    def is_valid(self, key: str) -> bool:
        return type(self).objects.key_generator.verify(key, self.hashed_key)

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


class APIKey(AbstractAPIKey):
    pass
