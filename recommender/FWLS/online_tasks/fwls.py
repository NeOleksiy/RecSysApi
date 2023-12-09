import time
from decimal import Decimal

from productApi.models import UserRating, Anime
from recommender.ContentBased.online_tasks import ContentBasedRecs
from recommender.collaborativeFiltering.online_tasks import CustomItemKNN
import pickle


class FeatureWeightedLinearStacking:
    def __init__(self):
        self.cb = ContentBasedRecs()
        self.cf = CustomItemKNN(neighborhood_size=10)

        self.wcb1 = Decimal(0.65221204)
        self.wcb2 = Decimal(-0.14638855)
        self.wcf1 = Decimal(-0.0062952)
        self.wcf2 = Decimal(0.09139193)
        self.intercept = Decimal(0)

    # функции для взвешивания алгоритмов рекомендации
    @staticmethod
    def fun1():
        return Decimal(1.0)

    @staticmethod
    def fun2(user_id):
        count = UserRating.objects.filter(user_id=user_id).count()
        if count > 2.0:
            return Decimal(1.0)
        return Decimal(0.0)

    # чтение весов линейной регрессии
    def set_save_path(self, save_path):
        with open(save_path + 'fwls_parameters.data', 'rb') as ub_file:
            parameters = pickle.load(ub_file)
            self.intercept = Decimal(parameters['intercept'])
            self.wcb1 = Decimal(parameters['cb1'])
            self.wcb2 = Decimal(parameters['cb2'])
            self.wcf1 = Decimal(parameters['cb1'])
            self.wcf2 = Decimal(parameters['cf2'])

    def recommend_items_by_ratings(self,
                                   user_id,
                                   active_user_items,
                                   num=6):

        cb_recs = self.cb.recommend_items_by_ratings(user_id, active_user_items, num * 3)
        cf_recs = self.cf.recommend_items_by_ratings(user_id, active_user_items, num * 3)

        return self.merge_predictions(user_id, cb_recs, cf_recs, num)

    def recommend_items(self, user_id, num=6):
        cb_recs = self.cb.recommend_items(user_id, num * 3)
        cf_recs = self.cf.recommend_items(user_id, num * 3)

        return self.merge_predictions(user_id, cb_recs, cf_recs, num)

    # получаем рекомендации и предикты от обоих алгоритмов рекомендации и получаем лучшие
    def merge_predictions(self, user_id, cb_recs, cf_recs, num):

        combined_recs = dict()

        for rec in cb_recs:
            movie_id = rec[0]
            pred = rec[1]['prediction']
            combined_recs[movie_id] = {'cb': pred}

        for rec in cf_recs:
            movie_id = rec[0]
            pred = rec[1]['prediction']
            if movie_id in combined_recs.keys():
                combined_recs[movie_id]['cf'] = pred
            else:
                combined_recs[movie_id] = {'cf': pred}

        fwls_preds = dict()

        for key, recs in combined_recs.items():

            if 'cb' not in recs.keys():
                recs['cb'] = self.cb.predict_score(user_id, key)

            if 'cf' not in recs.keys():
                recs['cf'] = self.cf.predict_score(user_id, key)

            pred = self.prediction(recs['cb'], recs['cf'], user_id)
            fwls_preds[key] = {'prediction': pred}
        sorted_items = sorted(fwls_preds.items(),
                              key=lambda item: -float(item[1]['prediction']))[:num]
        return sorted_items

    def predict_score(self, user_id, item_id):
        p_cb = self.cb.predict_score(user_id, item_id)
        p_cf = self.cf.predict_score(user_id, item_id)

        self.prediction(p_cb, p_cf, user_id)

    # взвешенная оценка
    def prediction(self, p_cb, p_cf, user_id):
        p = (self.wcb1 * self.fun1() * p_cb +
             self.wcb2 * self.fun2(user_id) * p_cb +
             self.wcf1 * self.fun1() * p_cf +
             self.wcf2 * self.fun2(user_id) * p_cf)
        print(self.wcb1, self.wcb2, self.wcf1, self.wcf2)
        return p + self.intercept
