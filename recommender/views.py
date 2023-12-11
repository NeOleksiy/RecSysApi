from decimal import Decimal
from math import sqrt

from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from productApi.models import Anime
from django.db.models import Count, Q
from rest_framework.views import APIView
from rest_framework.response import Response
from productApi.serializers import AnimeSerializer
import operator
from rest_framework import viewsets
from recommender.collaborativeFiltering.online_tasks import CustomItemKNN
from recommender.ContentBased.online_tasks import ContentBasedRecs
from recommender.FWLS.online_tasks.fwls import FeatureWeightedLinearStacking


# Create your views here.


def pearson(users, this_user, that_user):
    if this_user in users and that_user in users:
        this_user_avg = sum(users[this_user].values()) / len(users[this_user].values())
        that_user_avg = sum(users[that_user].values()) / len(users[that_user].values())

        all_movies = set(users[this_user].keys()) & set(users[that_user].keys())

        dividend = 0
        a_divisor = 0
        b_divisor = 0
        for movie in all_movies:

            if movie in users[this_user].keys() and movie in users[that_user].keys():
                a_nr = users[this_user][movie] - this_user_avg
                b_nr = users[that_user][movie] - that_user_avg
                dividend += a_nr * b_nr
                a_divisor += pow(a_nr, 2)
                b_divisor += pow(b_nr, 2)

        divisor = Decimal(sqrt(a_divisor) * sqrt(b_divisor))
        if divisor != 0:
            return Decimal(dividend) / divisor

    return 0


def jaccard(users, this_user, that_user):
    if this_user in users and that_user in users:
        intersect = set(users[this_user].keys()) & set(users[that_user].keys())
        union = set(users[this_user].keys()) | set(users[that_user].keys())
        return len(intersect) / Decimal(len(union))
    else:
        return 0


class CollaborateFilteringRecs(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user_id = request.user.user_id
        recs = CustomItemKNN().recommend_items(user_id)
        if len(recs) > 0:
            animies = []
            for anim in recs:
                anime_i = int(anim[0])
                anime = Anime.objects.get(anime_id=anime_i)
                anime_name = anime.name
                animies.append({anime_i: anime_name})
            return Response(animies)
        else:
            content = {'Ошибка рекомендаций': 'Недостаточное кол-во оценёных аниме'}
            return Response(content, status.HTTP_412_PRECONDITION_FAILED)


class ContentBasedRecommender(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user_id = request.user.user_id
        recs = ContentBasedRecs().recommend_items(user_id=user_id)
        if len(recs) > 0:
            animies = []
            for anim in recs:
                anime_i = int(anim[0])
                anime=Anime.objects.get(anime_id=anime_i)
                anime_name = anime.name
                animies.append({anime_i: anime_name})
            return Response(animies)
        else:
            content = {'Ошибка рекомендаций': 'Недостаточное кол-во оценёных аниме'}
            return Response(content, status.HTTP_412_PRECONDITION_FAILED)


class FWLS(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user_id = request.user.user_id
        recs = FeatureWeightedLinearStacking()
        recs.set_save_path('recommender/FWLS/offline_tasks/')
        recs = recs.recommend_items(user_id=user_id)
        if len(recs) > 0:
            animies = []
            for anim in recs:
                anime_i = int(anim[0])
                anime = Anime.objects.get(anime_id=anime_i)
                anime_name = anime.name
                animies.append({anime_i: anime_name})
            return Response(animies)
        else:
            content = {'Ошибка рекомендаций': 'Недостаточное кол-во оценёных аниме'}
            return Response(content, status.HTTP_412_PRECONDITION_FAILED)


class Popularity(viewsets.ViewSet):
    def __init__(self, n_recs=10, **kwargs):
        super().__init__(**kwargs)
        self.n_recs = n_recs

    def list(self, request):
        queryset = Anime.objects.all().order_by("-members")[:self.n_recs]
        serializer = AnimeSerializer(queryset, many=True)
        return Response(serializer.data)
