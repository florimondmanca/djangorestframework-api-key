from django.contrib import admin

from rest_framework_api_key.admin import APIKeyModelAdmin

from .models import Hero, HeroAPIKey


@admin.register(HeroAPIKey)
class HeroAPIKeyModelAdmin(APIKeyModelAdmin[HeroAPIKey]):
    pass


@admin.register(Hero)
class HeroModelAdmin(admin.ModelAdmin):
    pass
