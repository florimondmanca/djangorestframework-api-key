import typing

from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from .crypto import KeyGenerator, concatenate, split


class BaseAPIKeyManager(models.Manager):
    key_generator = KeyGenerator()

    def assign_key(self, obj: "AbstractAPIKey") -> str:
        try:
            key, prefix, hashed_key = self.key_generator.generate()
        except ValueError:  # Compatibility with < 1.4
            generate = typing.cast(
                typing.Callable[[], typing.Tuple[str, str]], self.key_generator.generate
            )
            key, hashed_key = generate()
            pk = hashed_key
            prefix, hashed_key = split(hashed_key)
        else:
            pk = concatenate(prefix, hashed_key)

        obj.id = pk
        obj.prefix = prefix
        obj.hashed_key = hashed_key

        return key

    def create_key(self, **kwargs: typing.Any) -> typing.Tuple["AbstractAPIKey", str]:
        # Prevent from manually setting the primary key.
        kwargs.pop("id", None)
        obj = self.model(**kwargs)
        key = self.assign_key(obj)
        obj.save()
        return obj, key

    def get_usable_keys(self) -> models.QuerySet:
        return self.filter(revoked=False)

    def get_from_key(self, key: str) -> "AbstractAPIKey":
        prefix, _, _ = key.partition(".")
        queryset = self.get_usable_keys()

        try:
            api_key = queryset.get(prefix=prefix)
        except self.model.DoesNotExist:
            raise  # For the sake of being explicit.

        if not api_key.is_valid(key):
            raise self.model.DoesNotExist("Key is not valid.")
        else:
            return api_key

    def is_valid(self, key: str) -> bool:
        try:
            api_key = self.get_from_key(key)
        except self.model.DoesNotExist:
            return False

        if api_key.has_expired:
            return False

        return True


class APIKeyManager(BaseAPIKeyManager):
    pass


class AbstractAPIKey(models.Model):
    objects = APIKeyManager()

    id = models.CharField(max_length=150, unique=True, primary_key=True, editable=False)
    prefix = models.CharField(max_length=8, unique=True, editable=False)
    hashed_key = models.CharField(max_length=150, editable=False)
    created = models.DateTimeField(auto_now_add=True, db_index=True)
    name = models.CharField(
        max_length=50,
        blank=False,
        default=None,
        help_text=(
            _(
                "A free-form name for the API key. "
                "Need not be unique. "
                "50 characters max."
            )
        ),
    )
    revoked = models.BooleanField(
        blank=True,
        default=False,
        help_text=(
            _(
                "If the API key is revoked, clients cannot use it anymore. "
                "(This cannot be undone.)"
            )
        ),
    )
    expiry_date = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name=_("Expires"),
        help_text=_("Once API key expires, clients cannot use it anymore."),
    )

    class Meta:  # noqa
        abstract = True
        ordering = ("-created",)
        verbose_name = "API key"
        verbose_name_plural = "API keys"

    def __init__(self, *args: typing.Any, **kwargs: typing.Any):
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
        key_generator = type(self).objects.key_generator
        valid = key_generator.verify(key, self.hashed_key)

        # Transparently update the key to use the preferred hasher
        # if it is using an outdated hasher.
        if valid and not key_generator.using_preferred_hasher(self.hashed_key):
            # Note that since the PK includes the hashed key,
            # they will be internally inconsistent following this upgrade.
            # See: https://github.com/florimondmanca/djangorestframework-api-key/issues/128
            self.hashed_key = key_generator.hash(key)
            self.save()

        return valid

    def clean(self) -> None:
        self._validate_revoked()

    def save(self, *args: typing.Any, **kwargs: typing.Any) -> None:
        self._validate_revoked()
        super().save(*args, **kwargs)

    def _validate_revoked(self) -> None:
        if self._initial_revoked and not self.revoked:
            raise ValidationError(
                _("The API key has been revoked, which cannot be undone.")
            )

    def __str__(self) -> str:
        return str(self.name)


class APIKey(AbstractAPIKey):
    pass
