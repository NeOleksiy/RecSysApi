from django.shortcuts import render
from decimal import Decimal
from math import sqrt
from django.http import JsonResponse
from productApi.models import *
from recommender.models import Similarity
from django.db.models import Avg, Count, Q
from rest_framework.views import APIView
from rest_framework.response import Response
import operator


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


class Similar_users(APIView):
    def get(self, request, user_id, sim_method):
        min = request.GET.get('min', 10)

        ratings = UserRating.objects.filter(user_id=user_id)
        sim_users = UserRating.objects.filter(anime_id__in=ratings.values('anime_id')) \
            .values('user_id').annotate(intersect=Count('user_id')).filter(intersect__gt=min)

        dataset = UserRating.objects.filter(user_id__in=sim_users.values('user_id'))

        users = {u['user_id']: {} for u in sim_users}

        for row in dataset.values():
            user = row['user_id_id']
            anime = row['anime_id_id']
            rating = row['rating']
            if user in users.keys():
                users[user][anime] = rating
        similarity = dict()
        switcher = {
            'jaccard': jaccard,
            'pearson': pearson,

        }

        for user in sim_users:

            func = switcher.get(sim_method, lambda: "nothing")
            s = func(users, user_id, user['user_id'])

            if s > 0.2:
                similarity[user['user_id']] = round(s, 2)
        topn = sorted(similarity.items(), key=operator.itemgetter(1), reverse=True)[:10]

        data = {
            'user_id': user_id,
            'anime_rated': len(users[user_id]),
            'type': sim_method,
            'topn': topn,
            'similarity': topn,
        }

        return Response(data)


class OnlineCollaborateFiltering(APIView):
    def get(self, request, user_id):
        active_user_items = UserRating.objects.filter(user_id=user_id).order_by('-rating')
        if len(active_user_items) == 0:
            return Response({})
        anime_ids = {anime['anime_id_id']: anime['rating']
                     for anime in active_user_items.values()}
        user_mean = Decimal(sum(anime_ids.values()) / len(anime_ids))
        candidate_items = Similarity.objects.filter(Q(source__in=anime_ids.keys())
                                                    & ~Q(target__in=anime_ids.keys()))
        candidate_items = candidate_items.order_by('-similarity')[:25]
        recs = dict()
        for candidate in candidate_items:
            target = candidate.target

            pre = 0
            sim_sum = 0

            rated_items = [i for i in candidate_items if i.target == target][:15]
            if len(rated_items) > 1:
                for sim_item in rated_items:
                    key = sim_item.source
                    r = Decimal(anime_ids[int(key)] - user_mean)
                    pre += sim_item.similarity * r
                    sim_sum += sim_item.similarity
                if sim_sum > 0:
                    recs[target] = {'prediction': Decimal(user_mean) + pre / sim_sum,
                                    'sim_items': [r.source for r in rated_items]}

        sorted_items = sorted(recs.items(), key=lambda item: -float(item[1]['prediction']))[:10]
        return Response(sorted_items)
