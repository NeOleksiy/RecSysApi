from django.shortcuts import render
from rest_framework.generics import CreateAPIView
from rest_framework.views import APIView
from collector.serializers import ConversionSerializer
from collector.models import Logs


# Create your views here.


class Logging(CreateAPIView):
    queryset = Logs.objects.all()
    serializer_class = ConversionSerializer


