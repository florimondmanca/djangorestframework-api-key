import typing

from django.core.exceptions import ValidationError
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils import timezone

from .crypto import concatenate, KeyGenerator, split


class ScopeManager(models.Manager):
    def get_from_label(self, label: str) -> "Scope":
        app_label, model, code = self.model.parse_label(label)
        content_type = ContentType.objects.get(app_label=app_label, model=model)
        return self.get(content_type=content_type, code=code)


class Scope(models.Model):
    objects = ScopeManager()
    content_type = models.ForeignKey(
        ContentType, models.CASCADE, verbose_name="content type"
    )  # type: ContentType
    code = models.CharField(max_length=64)
    name = models.CharField(max_length=64)

    class Meta:
        unique_together = [("content_type", "code")]
        ordering = ["content_type__app_label", "content_type__model", "code"]

    _LABEL_FORMAT = "{app_label}.{model}.{code}"

    @property
    def label(self) -> str:
        return Scope._LABEL_FORMAT.format(
            app_label=self.content_type.app_label,  # pylint: disable=no-member
            model=self.content_type.model,
            code=self.code,
        )

    @classmethod
    def parse_label(cls, label: str) -> typing.Tuple[str, str, str]:
        try:
            app_label, model, code = label.split(".")
        except ValueError:
            raise ValueError(
                "'label' must be formatted as '{}', got '{}'".format(
                    cls._LABEL_FORMAT, label
                )
            )
        return app_label, model, code

    def natural_key(self) -> typing.Tuple[str]:
        # Used by Django serialization.
        # See: https://docs.djangoproject.com/en/2.2/topics/serialization/#serialization-of-natural-keys
        # NOTE: this implementation is mostly copied from Django's `Permission`.
        return (
            self.code,
        ) + self.content_type.natural_key()  # pylint: disable=no-member

    natural_key.dependencies = ["contenttypes.contenttype"]

    def __str__(self) -> str:
        return self.label


def _get_scopes_field(
    related_name: str, related_query_name: str
) -> models.ManyToManyField:
    return models.ManyToManyField(
        Scope,
        verbose_name="scopes",
        blank=True,
        help_text="Specific scopes for this API key",
        related_name=related_name,
        related_query_name=related_query_name,
    )


class ScopesMixin(models.Model):
    scopes = _get_scopes_field(
        # See: https://docs.djangoproject.com/en/2.2/topics/db/models/#be-careful-with-related-name-and-related-query-name
        related_name="%(app_label)s_%(class)s_set",
        related_query_name="%(app_label)s_%(class)s",
    )  # type: models.Manager

    def get_scopes(self) -> typing.Set[str]:
        cache_name = "_scopes_cache"
        if not hasattr(self, cache_name):
            scopes = self.scopes.all()  # pylint: disable=no-member
            cache = {
                scope.label for scope in scopes.select_related("content_type")
            }
            setattr(self, cache_name, cache)
        return getattr(self, cache_name)

    def has_scope(self, name: str) -> bool:
        return name in self.get_scopes()

    def has_scopes(self, names: typing.List[str]) -> bool:
        return all(self.has_scope(name) for name in names)

    class Meta:
        abstract = True


class BaseAPIKeyManager(models.Manager):
    key_generator = KeyGenerator()

    def assign_key(self, obj: "AbstractAPIKey") -> str:
        try:
            key, prefix, hashed_key = self.key_generator.generate()
        except ValueError:  # Compatibility with < 1.4
            key, hashed_key = self.key_generator.generate()
            pk = hashed_key
            prefix, hashed_key = split(hashed_key)
        else:
            pk = concatenate(prefix, hashed_key)

        obj.id = pk
        obj.prefix = prefix
        obj.hashed_key = hashed_key

        return key

    def create_key(self, **kwargs) -> typing.Tuple["AbstractAPIKey", str]:
        # Prevent from manually setting the primary key.
        kwargs.pop("id", None)
        obj = self.model(**kwargs)  # type: AbstractAPIKey
        key = self.assign_key(obj)
        obj.save()
        return obj, key

    def get_usable_keys(self) -> models.QuerySet:
        return self.filter(revoked=False)

    def get_from_secret(self, key: str) -> "AbstractAPIKey":
        prefix, _, _ = key.partition(".")
        queryset = self.get_usable_keys()
        return queryset.get(prefix=prefix)

    def is_valid(self, key: str) -> bool:
        try:
            api_key = self.get_from_secret(key)
        except self.model.DoesNotExist:
            return False

        if not api_key.is_valid(key):
            return False

        if api_key.has_expired:
            return False

        return True


class APIKeyManager(BaseAPIKeyManager):
    pass


class AbstractAPIKey(ScopesMixin, models.Model):
    objects = APIKeyManager()

    id = models.CharField(
        max_length=100, unique=True, primary_key=True, editable=False
    )
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

    _has_expired.short_description = "Has expired"
    _has_expired.boolean = True
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
    scopes = _get_scopes_field(
        related_name="apikey_set", related_query_name="apikey"
    )  # type: models.Manager
