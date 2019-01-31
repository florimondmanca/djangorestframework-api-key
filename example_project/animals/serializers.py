"""Example serializers."""

from rest_framework import serializers

from .models import Animal


class AnimalSerializer(serializers.ModelSerializer):
    """Serializer for animals."""

    class Meta:
        model = Animal
        fields = ("id", "name", "noise")
