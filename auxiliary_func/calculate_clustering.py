import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "RecSystem.settings")

import django
from django.db.models import Count
from tqdm import tqdm
from scipy.sparse import dok_matrix
from sklearn.cluster import KMeans
import matplotlib as mlt

mlt.use('TkAgg')

import numpy as np

django.setup()

from productApi.models import UserRating, Cluster


class UserClusterCalculator(object):

    def calculate(self, k=23):
        print("training k-means clustering")

        user_ids, user_ratings = self.load_data()

        kmeans = KMeans(n_clusters=k)

        clusters = kmeans.fit(user_ratings.tocsr())

        self.save_clusters(clusters, user_ids)

        return clusters

    @staticmethod
    def save_clusters(clusters, user_ids):
        print("saving clusters")
        Cluster.objects.all().delete()
        for i, cluster_label in enumerate(clusters.labels_):
            Cluster(
                cluster_id=cluster_label,
                user_id=user_ids[i]['user_id']).save()

    @staticmethod
    def load_data():
        print('loading data')
        user_ids = list(
            UserRating.objects.values('user_id')
            .annotate(anime_count=Count('anime_id'))
            .order_by('-anime_count'))
        content_ids = list(UserRating.objects.values('anime_id').distinct())
        content_map = {content_ids[i]['anime_id']: i
                       for i in range(len(content_ids))}
        num_users = len(user_ids)
        user_ratings = dok_matrix((num_users,
                                   len(content_ids)),
                                  dtype=np.float32)
        for i in tqdm(range(num_users)):
            # each user corresponds to a row, in the order of all_user_names
            ratings = UserRating.objects.filter(user_id=user_ids[i]['user_id'])
            for user_rating in ratings.values():
                anime = user_rating['anime_id_id']
                rating = user_rating['rating']
                user_ratings[i, content_map[anime]] = rating
        print('data loaded')

        return user_ids, user_ratings


if __name__ == '__main__':
    print("Calculating user clusters...")

    cluster = UserClusterCalculator()
    cluster.calculate(23)
