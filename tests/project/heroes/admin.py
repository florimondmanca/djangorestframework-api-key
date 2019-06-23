from django.contrib import admin
from rest_framework_api_key.admin import APIKeyModelAdmin

from .models import HeroAPIKey


@admin.register(HeroAPIKey)
class HeroAPIKeyModelAdmin(APIKeyModelAdmin):
    pass
