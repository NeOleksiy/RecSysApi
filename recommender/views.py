from django.shortcuts import render
from decimal import Decimal
from math import sqrt
from django.http import JsonResponse
from productApi.models import *
from django.db.models import Avg, Count
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
            return Decimal(dividend / (sqrt(a_divisor) * sqrt(b_divisor)))

    return 0


def jaccard(users, this_user, that_user):
    print(users, this_user, that_user)
    if this_user in users and that_user in users:
        intersect = set(users[this_user].keys()) & set(users[that_user].keys())
        print(intersect)
        union = set(users[this_user].keys()) | set(users[that_user].keys())
        print(union)
        return len(intersect) / Decimal(len(union))
    else:
        return 0


class Similar_users(APIView):
    def get(self, request, user_id, sim_method):
        min = request.GET.get('min', 1)
        print(min)

        ratings = UserRating.objects.filter(user_id=user_id)
        sim_users = UserRating.objects.filter(anime_id__in=ratings.values('anime_id')) \
            .values('user_id') \
            .annotate(intersect=Count('user_id')).filter(intersect__gt=min)

        dataset = UserRating.objects.filter(user_id__in=sim_users.values('user_id'))
        print(dataset.values())

        users = {u['user_id']: {} for u in sim_users}

        for row in dataset.values():
            user = row['user_id_id']
            anime = row['anime_id_id']
            rating = row['rating']
            if user in users.keys():
                users[user][anime] = rating
        print(users[14096])
        similarity = dict()
        print(users)
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
            'anime': users[user_id].keys(),
            'type': sim_method,
            'topn': topn,
            'similarity': topn,
        }

        return Response(data)
