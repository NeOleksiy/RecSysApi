from django.db import models
from django.contrib.auth.models import AbstractUser


class Gender(models.TextChoices):
    MALE = 'M', 'Мужской'
    FEMALE = 'F', 'Женский'


class User(AbstractUser):
    user_id = models.IntegerField(primary_key=True, unique=True)
    user_name = models.CharField(max_length=32, default='Radislav')
    email = models.EmailField(max_length=64, default='nikto@gmail.com')

    def __str__(self):
        return f'{self.user_id}'


class UserAttribute(models.Model):
    user = models.ForeignKey(to=User, on_delete=models.CASCADE)
    age = models.PositiveSmallIntegerField(default=22)
    gender = models.CharField(max_length=1, choices=Gender.choices, default='M')

    def __str__(self):
        return self.user.user_name




