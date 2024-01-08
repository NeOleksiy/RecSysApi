from django.urls import path, include

from productApi.views import AnimeViewSet, GenresFiltering
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'anime', AnimeViewSet, basename='AnimeList')
urlpatterns = [
    path('anime/', include(router.urls)),
    path('genresFilter/', GenresFiltering.as_view(), name='filter genres')
]
