from rest_framework import serializers
from collector.models import Logs, Event


class ConversionSerializer(serializers.ModelSerializer):
    user_id = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Logs
        fields = ['user_id', 'content_id', 'event']
