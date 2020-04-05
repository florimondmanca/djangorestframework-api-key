import typing

from django.db import models

from rest_framework_api_key.models import AbstractAPIKey, BaseAPIKeyManager

T = typing.TypeVar("T")


class Hero(models.Model):
    objects = models.Manager()
    name = models.CharField(max_length=64)
    retired = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = "heroes"

    def __str__(self) -> str:
        return self.name


class HeroAPIKeyManager(BaseAPIKeyManager["HeroAPIKey"]):
    def get_usable_keys(self) -> "models.QuerySet[HeroAPIKey]":
        return super().get_usable_keys().filter(hero__retired=False)


class HeroAPIKey(AbstractAPIKey):
    objects = HeroAPIKeyManager()
    hero = models.ForeignKey(Hero, on_delete=models.CASCADE, related_name="api_keys")

    class Meta(AbstractAPIKey.Meta):
        verbose_name = "Hero API key"
        verbose_name_plural = "Hero API keys"


# A straight subclass to verify that defining `.objects` is not required.
class MyAPIKey(AbstractAPIKey):
    pass
