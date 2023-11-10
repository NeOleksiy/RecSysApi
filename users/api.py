from django.shortcuts import render
from rest_framework import viewsets
from rest_framework import permissions
from users.models import User
from users.serializers import UserSerializer


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint for posts
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
# Create your views here.
