from django.db import models
from users.models import *
from productApi.models import *


# Create your models here.
class Event(models.TextChoices):
    open_site = 'open site'  # Открыл главную страницу сайта
    open_new_page = 'Opened another page of the site'  # Открыл какую какую либо страницу сайта
    open_product_page = 'open the product page'  # Открыл страницу товара
    add_to_list = 'add to list'  # Добавил в список для просмотра
    watched = 'watched'  # Посмотрел и отметил как просмотренное
    rated = 'rated'  # Оценил


class Logs(models.Model):
    user_id = models.ForeignKey(to=User, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    content_id = models.ForeignKey(to=Anime, on_delete=models.CASCADE, blank=True, null=True)
    event = models.CharField(max_length=200, choices=Event.choices)

    def __str__(self):
        return f'User {self.user_id} make event: {self.event}'
