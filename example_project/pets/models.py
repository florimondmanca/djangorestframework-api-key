from django.db import models


class Pet(models.Model):
    ANIMAL_CHOICES = [("DOG", "Dog"), ("CAT", "Cat")]
    animal = models.CharField(max_length=100, choices=ANIMAL_CHOICES)
    nickname = models.CharField(max_length=100)

    def __str__(self):
        return str(self.nickname)
