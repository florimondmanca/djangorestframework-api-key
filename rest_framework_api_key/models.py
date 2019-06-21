from typing import Tuple

from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from . import validators
from .crypto import KeyGenerator


class BaseAPIKeyManager(models.Manager):
    key_generator = KeyGenerator()

    def assign_key(self, obj: "AbstractAPIKey") -> str:
        key, hashed_key = self.key_generator.generate()
        obj.id = hashed_key
        return key

    def create_key(self, **kwargs) -> Tuple["AbstractAPIKey", str]:
        # Prevent from manually setting the primary key.
        kwargs.pop("id", None)
        obj = self.model(**kwargs)  # type: AbstractAPIKey
        key = self.assign_key(obj)
        obj.save()
        return obj, key

    def is_valid(self, key: str) -> tuple:
        prefix, _, _ = key.partition(".")

        try:
            api_key = self.get(
                id__startswith=prefix, revoked=False
            )  # type: AbstractAPIKey
        except (self.model.DoesNotExist, self.model.MultipleObjectsReturned):
            return False, None

        if not api_key.is_valid(key):
            return False, api_key

        if api_key.has_expired:
            return False, api_key

        return True, api_key


class APIKeyManager(BaseAPIKeyManager):
    pass


class APIKeyGroup(models.Model):
    name = models.CharField(
        max_length=50,
        unique=True,
        help_text='The name of the API key group',
    )

    endpoint_permissions = models.ManyToManyField(
        'EndpointPermission',
        related_name='api_key_groups',
        blank=True,
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'API key group'
        verbose_name_plural = 'API key groups'


class AbstractAPIKey(models.Model):
    objects = APIKeyManager()

    id = models.CharField(max_length=100, unique=True, primary_key=True)
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

    group = models.ForeignKey(
        APIKeyGroup,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
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

    def _prefix(self) -> str:
        return self.pk.partition(".")[0]

    _prefix.short_description = "Prefix"
    prefix = property(_prefix)

    def _has_expired(self) -> bool:
        if self.expiry_date is None:
            return False
        return self.expiry_date < timezone.now()

    _has_expired.short_description = "Has expired"
    _has_expired.boolean = True
    has_expired = property(_has_expired)

    def is_valid(self, key: str) -> bool:
        _, _, hashed_key = self.pk.partition(".")
        return type(self).objects.key_generator.verify(key, hashed_key)

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


class EndpointPermission(models.Model):
    METHODS = [
        'CONNECT',
        'DELETE',
        'GET',
        'HEAD',
        'OPTIONS',
        'PATCH',
        'POST',
        'PUT',
        'TRACE',
    ]
    METHOD_CHOICES = [(method, method) for method in METHODS]

    path = models.CharField(
        max_length=100,
        help_text=('A regex matching the URL path. '
                   'This should begin with / and include the version, eg "/v1/time"'),
        validators=[validators.validate_regex_pattern],
    )
    method = models.CharField(
        max_length=100,
        choices=METHOD_CHOICES,
        default='',
    )

    def __str__(self):
        return f'{self.method} {self.path}'

    class Meta:
        verbose_name = 'Endpoint permission'
        verbose_name_plural = 'Endpoint permissions'
        unique_together = ('path', 'method')
