from django.db import models
from rest_framework_api_key.models import AbstractAPIKey, BaseAPIKeyManager


class Hero(models.Model):
    objects = models.Manager()
    name = models.CharField(max_length=64)
    retired = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = "heroes"

    def __str__(self):
        return self.name


class HeroAPIKeyManager(BaseAPIKeyManager):
    def get_usable_keys(self):
        return super().get_usable_keys().filter(hero__retired=False)


class HeroAPIKey(AbstractAPIKey):
    objects = HeroAPIKeyManager()
    hero = models.ForeignKey(
        Hero, on_delete=models.CASCADE, related_name="api_keys"
    )

    class Meta(AbstractAPIKey.Meta):
        verbose_name = "Hero API key"
        verbose_name_plural = "Hero API keys"
