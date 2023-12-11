import os

from decimal import Decimal

from django.db.models import Q

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "RecSystem.settings")

import django

django.setup()

from recommender.models import Similarity
from productApi.models import UserRating, Anime


class CustomItemKNN:
    def __init__(self, similarity_n=100, neighborhood_size=10, rec_item_n=10, min_sim=0.0):
        self.similarity_n = similarity_n  # Кол-во схожих аниме для оценённых пользователем аниме
        self.neighborhood_size = neighborhood_size  # Кол-во соседей каждому аниме
        self.rec_item_n = rec_item_n  # Кол-во рекомендаций (до rec_item_n)
        self.min_sim = min_sim

    def recommend_items(self, user_id, num=6):

        active_user_items = UserRating.objects.filter(user_id=user_id).order_by('-rating')[:100]

        return self.recommend_items_by_ratings(user_id, active_user_items.values())[:num]

    def recommend_items_by_ratings(self, user_id, active_user_items,
                                   num=6):

        if len(active_user_items) == 0:
            return {}
        anime_ids = {anime['anime_id_id']: (anime['rating'] if anime['rating'] != -1
                                            else Anime.objects.get(anime_id=anime['anime_id_id']).rating)
                     for anime in active_user_items.values()}
        user_mean = Decimal(sum(anime_ids.values()) / len(anime_ids))
        # Для каждого оценённого аниме пользователем берём подобные ему из таблицы схожих элементов
        candidate_items = Similarity.objects.filter(Q(source__in=anime_ids.keys())
                                                    & ~Q(target__in=anime_ids.keys())
                                                    & Q(similarity__gt=self.min_sim))
        candidate_items = candidate_items.order_by('-similarity')[:self.similarity_n]
        recs = dict()
        for candidate in candidate_items:
            target = candidate.target

            pre = 0
            sim_sum = 0
            # Отбор аниме по сходству методом top N
            rated_items = [i for i in candidate_items if i.target == target][:self.neighborhood_size]
            if len(rated_items) > 1:
                for sim_item in rated_items:
                    key = sim_item.source
                    r = Decimal(anime_ids[int(key)] - user_mean)
                    pre += sim_item.similarity * r
                    sim_sum += sim_item.similarity
                if sim_sum > 0:
                    # target = Anime.objects.get(anime_id=target).name
                    # Вычисление средневзвешенной оценки пользователя из отобранных аниме
                    recs[target] = {'prediction': Decimal(user_mean) + pre / sim_sum,
                                    'sim_items': [r.source for r in rated_items]}

        sorted_items = sorted(recs.items(), key=lambda item: -float(item[1]['prediction']))[:num]
        return sorted_items

    def predict_score(self, user_id, item_id):
        user_items = (UserRating.objects.filter(user_id=user_id)
                      .exclude(anime_id=item_id)
                      .order_by('-rating').values()[:self.similarity_n])

        anime_ids = {anime['anime_id_id']: (anime['rating'] if anime['rating'] != -1
                                            else Anime.objects.get(anime_id=anime['anime_id_id']).rating)
                     for anime in user_items.values()}
        user_mean = sum(anime_ids.values()) / len(anime_ids)

        sims = Similarity.objects.filter(source__in=anime_ids.keys()) \
                   .filter(target=item_id) \
                   .exclude(source=item_id).distinct().order_by('-similarity')[:self.similarity_n]

        pre = 0
        sim_sum = 0
        prediction = Decimal(0.0)

        if len(sims) > 0:
            for sim_item in sims:
                r = Decimal(anime_ids[int(sim_item.source)] - user_mean)
                pre += sim_item.similarity * r
                sim_sum += sim_item.similarity

            prediction = Decimal(user_mean) + pre / sim_sum
        return prediction
