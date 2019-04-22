"""Example admin."""

from django.contrib import admin

from .models import Pet


@admin.register(Pet)
class PetAdmin(admin.ModelAdmin):
    """Admin panel for pets."""

    list_display = ("nickname", "animal", "id")
