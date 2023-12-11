from rest_framework import serializers

from productApi.models import UserRating
from users.models import User
from django.db import models


class UserSerializer(serializers.ModelSerializer):
    user_id = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = User
        fields = ('user_id', 'username', 'email', 'password')

    def create(self, validated_data):
        # Получаем максимальное значение user_id
        max_user_id = User.objects.aggregate(models.Max('user_id'))['user_id__max'] or 0
        validated_data['user_id'] = max_user_id + 1

        # Создаем пользователя
        user = User.objects.create(**validated_data)
        return user


class UserRatingSerializer(serializers.ModelSerializer):
    user_id = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = UserRating
        fields = '__all__'
