"""Example models."""

from django.db import models


class Animal(models.Model):
    """Represents an animal."""

    name = models.CharField(max_length=100)
    noise = models.CharField(max_length=100)

    def __str__(self):
        return str(self.name)
