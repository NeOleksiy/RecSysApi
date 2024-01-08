from rest_framework import viewsets
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser, IsAuthenticatedOrReadOnly

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from productApi.models import Anime, Genre
from productApi.serializers import AnimeSerializer


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


class GenresFiltering(ListAPIView):
    queryset = Anime.objects.all()
    serializer_class = AnimeSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'genre': openapi.Schema(type=openapi.TYPE_STRING),
            'genres': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_STRING)),
        }
    ))
    def get_queryset(self):
        genre_name = self.request.data.get('genre_name')
        print(genre_name)
        if genre_name is None:
            return Anime.objects.all()
        genre = Genre.objects.get(genre=genre_name)
        filtering_anime = Anime.objects.filter(genre=genre).distinct()
        return filtering_anime
