from decimal import Decimal

from django.db.models import Q

from productApi.models import UserRating, Anime
from recommender.models import TfIdfMatrix


class ContentBasedRecs:

    def __init__(self, min_sim=0.1):

        self.min_sim = min_sim
        self.max_candidates = 100

    def recommend_items(self, user_id, num=6):

        active_user_items = UserRating.objects.filter(user_id=user_id).order_by('-rating')[:100]

        return self.recommend_items_by_ratings(user_id, active_user_items.values(), num)

    @staticmethod
    def seeded_rec(content_ids, take=6):
        data = TfIdfMatrix.objects.filter(row_id__in=content_ids) \
                   .order_by('-tfidf_sim') \
                   .values('col_id', 'tfidf_sim')[:take]
        return list(data)

    def recommend_items_by_ratings(self,
                                   user_id,
                                   active_user_items,
                                   num=6):
        if len(active_user_items) == 0:
            return {}

        anime_ids = {anime['anime_id_id']: (anime['rating'] if anime['rating'] != -1
                                            else Anime.objects.get(anime_id=anime['anime_id_id']).rating)
                     for anime in active_user_items.values()}

        user_mean = sum(anime_ids.values()) / len(anime_ids)
        sims = TfIdfMatrix.objects.filter(Q(row_id__in=anime_ids.keys())
                                          & ~Q(col_id__in=anime_ids.keys())).order_by('-tfidf_sim')

        sims = sims[:self.max_candidates]
        recs = dict()
        targets = set(s.col_id for s in sims)
        for target in targets:

            pre = 0
            sim_sum = 0

            rated_items = [i for i in sims if i.col_id == target]#[:10]

            if len(rated_items) > 0:

                for sim_item in rated_items:
                    r = Decimal(anime_ids[int(sim_item.row_id)] - user_mean)
                    pre += sim_item.tfidf_sim * r
                    sim_sum += sim_item.tfidf_sim

                if sim_sum > 0:
                    # try:
                    #     target = Anime.objects.get(anime_id=target).name
                    # except Anime.DoesNotExist:
                    #     continue
                    recs[target] = {'prediction': Decimal(user_mean) + pre / sim_sum,
                                    'sim_items': [r.row_id for r in rated_items]}

        return sorted(recs.items(), key=lambda item: -float(item[1]['prediction']))[:num]

    def predict_score(self, user_id, item_id):
        user_items = (UserRating.objects.filter(user_id=user_id)
                      .exclude(anime_id=item_id)
                      .order_by('-rating').values()[:100])

        anime_ids = {anime['anime_id_id']: (anime['rating'] if anime['rating'] != -1
                                            else Anime.objects.get(anime_id=anime['anime_id_id']).rating)
                     for anime in user_items}
        user_mean = sum(anime_ids.values()) / len(anime_ids)

        sims = TfIdfMatrix.objects.filter(Q(row_id__in=anime_ids.keys())
                                          & Q(col_id=item_id)
                                          & Q(tfidf_sim__gt=self.min_sim)).order_by('-tfidf_sim')

        pre = 0
        sim_sum = 0
        prediction = Decimal(0.0)

        if len(sims) > 0:
            for sim_item in sims:
                r = Decimal(anime_ids[int(sim_item.row_id)] - user_mean)
                pre += sim_item.tfidf_sim * r
                sim_sum += sim_item.tfidf_sim

            prediction = Decimal(user_mean) + pre / sim_sum
        return prediction


