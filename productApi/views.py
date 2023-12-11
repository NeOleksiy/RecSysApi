from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAdminUser, IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from productApi.models import Anime, Genre
from productApi.serializers import AnimeSerializer
from users.models import User
from users.serializers import UserSerializer


# Create your views here.
class AnimeViewSet(viewsets.ModelViewSet):
    queryset = Anime.objects.all()
    serializer_class = AnimeSerializer

    def get_permissions(self):

        if self.action == 'list':
            permission_classes = [IsAuthenticatedOrReadOnly]
        else:
            permission_classes = [IsAdminUser]
        return [permission() for permission in permission_classes]

    @action(detail=False, methods=['get'])
    def genres_filter(self, request, **kwargs):
        genres = Genre.objects.filter(genre=self.kwargs['genres'])
        filtering_anime = Anime.objects.filter(genres__in=genres).distinct()
        serialized_anime = AnimeSerializer(data=filtering_anime)
        if serialized_anime.is_valid():
            return Response({genres.values()['genre']: serialized_anime})
        else:
            return Response(serialized_anime.errors,
                            status=status.HTTP_400_BAD_REQUEST)


