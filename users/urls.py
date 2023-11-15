from django.urls import path
from . import api

urlpatterns = [
    path('user', api.UserViewSet.as_view({'get': 'list'}), name='api_user'),
]
