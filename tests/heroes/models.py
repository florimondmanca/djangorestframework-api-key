from django.db import models
from rest_framework_api_key.models import BaseAPIKey


class Hero(models.Model):
    objects = models.Manager()


class HeroAPIKey(BaseAPIKey):
    hero = models.OneToOneField(
        Hero, on_delete=models.CASCADE, related_name="api_key"
    )
