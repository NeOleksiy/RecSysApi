from rest_framework import serializers
from productApi.models import Anime


class AnimeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Anime
        fields = ('anime_id', 'name')