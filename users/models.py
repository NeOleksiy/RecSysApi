from django.db import models
from django.contrib.auth.models import AbstractUser


class Gender(models.TextChoices):
    MALE = 'M', 'Мужской'
    FEMALE = 'F', 'Женский'


class User(AbstractUser):
    username = models.CharField(max_length=32,unique=True)
    email = models.CharField(max_length=64)

    def __str__(self):
        return self.username


class UserAttribute(models.Model):
    user = models.ForeignKey(to=User, on_delete=models.CASCADE)
    age = models.PositiveSmallIntegerField()
    gender = models.CharField(max_length=1, choices=Gender.choices)

    def __str__(self):
        return self.user

