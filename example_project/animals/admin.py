"""Example admin."""

from django.contrib import admin

from .models import Animal


@admin.register(Animal)
class AnimalAdmin(admin.ModelAdmin):
    """Admin panel for animals."""

    list_display = ('name', 'noise', 'id')
