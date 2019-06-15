from django.db import models
from rest_framework_api_key.models import AbstractAPIKey


class Hero(models.Model):
    objects = models.Manager()


class HeroAPIKey(AbstractAPIKey):
    hero = models.OneToOneField(
        Hero, on_delete=models.CASCADE, related_name="api_key"
    )
