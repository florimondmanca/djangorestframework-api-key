from django.db import models
from rest_framework_api_key.models import AbstractAPIKey, BaseAPIKeyManager


class Hero(models.Model):
    objects = models.Manager()
    retired = models.BooleanField(default=False)


class HeroAPIKeyManager(BaseAPIKeyManager):
    def get_usable_keys(self):
        return super().get_usable_keys().filter(hero__retired=False)


class HeroAPIKey(AbstractAPIKey):
    objects = HeroAPIKeyManager()
    hero = models.OneToOneField(
        Hero, on_delete=models.CASCADE, related_name="api_key"
    )
