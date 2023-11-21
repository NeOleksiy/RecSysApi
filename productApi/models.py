from django.db import models
from users.models import User


class Type(models.TextChoices):
    TV = 'TV'
    OVA = 'OVA'
    MOVIE = 'Movie'
    SPECIAL = 'Special'
    ONA = 'ONA'


class Genre(models.Model):
    genre = models.CharField(max_length=128)

    def __str__(self):
        return self.genre


# Сам продукт(в нашем слуае аниме)
class Anime(models.Model):
    anime_id = models.PositiveIntegerField(primary_key=True)
    name = models.CharField(max_length=300)
    genre = models.ManyToManyField(to=Genre, blank=True, related_name='genres')
    type = models.CharField(max_length=8, choices=Type.choices)
    episodes = models.PositiveIntegerField()
    rating = models.DecimalField(max_digits=3, decimal_places=1)
    members = models.PositiveBigIntegerField()

    def __str__(self):
        return f'{self.name} with id={self.anime_id}'


# Оценки пользователей
class UserRating(models.Model):
    user_id = models.ForeignKey(to=User, on_delete=models.CASCADE)
    anime_id = models.ForeignKey(to=Anime, on_delete=models.CASCADE)
    rating = models.SmallIntegerField(default=-1)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user_id', 'anime_id'], name='user_anime_rating'
            )
        ]

    def __str__(self):
        return f'{self.anime_id} with rating {self.rating}'


# Пользователи определённые на кластеры
class Cluster(models.Model):
    cluster_id = models.IntegerField()
    user_id = models.IntegerField()

    def __str__(self):
        return "User {} in cluster {}".format(self.user_id, self.cluster_id)


# Список просмотренных
class WatchedList(models.Model):
    user_id = models.ForeignKey(to=User, on_delete=models.CASCADE)
    watch_list = models.JSONField(default=dict, blank=True, null=True)

    def __str__(self):
        return "User {} list {}".format(self.user_id, self.watch_list)

    @classmethod
    def add_in_scheduled(cls, anime_id):
        WatchedList.watch_list[anime_id] = 'not viewed'
