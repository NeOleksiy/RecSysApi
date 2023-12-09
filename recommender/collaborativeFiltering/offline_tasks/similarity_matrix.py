import os
import pandas as pd
import logging
from tqdm import tqdm
from sklearn.metrics.pairwise import cosine_similarity
from scipy.sparse import coo_matrix
from datetime import datetime

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "RecSystem.settings")

import django

django.setup()

from recommender.models import Similarity
from productApi.models import UserRating
from RecSystem import settings

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.DEBUG)
logger = logging.getLogger('Item simialarity calculator')


class ItemSimilarityMatrixBuilder(object):

    def __init__(self, min_overlap=10, min_sim=0.2):
        self.min_overlap = min_overlap
        self.min_sim = min_sim
        self.db = settings.DATABASES['default']['ENGINE']

    def build(self, ratings, save=True):

        logger.info("Calculating similarities ... using {} ratings".format(len(ratings)))
        start_time = datetime.now()

        logger.info("Creating ratings matrix")
        ratings['rating'] = ratings['rating'].astype(float)
        ratings['avg'] = ratings.groupby('user_id')['rating'].transform(lambda x: normalize(x))

        ratings['avg'] = ratings['avg'].astype(float)
        ratings['user_id'] = ratings['user_id'].astype('category')
        ratings['anime_id'] = ratings['anime_id'].astype('category')

        coo = coo_matrix((ratings['avg'].astype(float),
                          (ratings['anime_id'].cat.codes.copy(),
                           ratings['user_id'].cat.codes.copy())))

        logger.info("Calculating overlaps between the items")
        overlap_matrix = coo.astype(bool).astype(int).dot(coo.transpose().astype(bool).astype(int))

        number_of_overlaps = (overlap_matrix > self.min_overlap).count_nonzero()
        logger.info("Overlap matrix leaves {} out of {} with {}".format(number_of_overlaps,
                                                                        overlap_matrix.count_nonzero(),
                                                                        self.min_overlap))

        logger.info("Rating matrix (size {}x{}) finished, in {} seconds".format(coo.shape[0],
                                                                                coo.shape[1],
                                                                                datetime.now() - start_time))

        sparsity_level = 1 - (ratings.shape[0] / (coo.shape[0] * coo.shape[1]))
        logger.info("Sparsity level is {}".format(sparsity_level))
        start_time = datetime.now()
        cor = cosine_similarity(coo, dense_output=False)
        # cor = rp.corr(method='pearson', min_periods=self.min_overlap)
        # cor = (cosine(rp.T))
        cor = cor.multiply(cor > self.min_sim)
        cor = cor.multiply(overlap_matrix > self.min_overlap)
        anime_list = dict(enumerate(ratings['anime_id'].cat.categories))
        print(cor, anime_list)
        logger.info('Correlation is finished, done in {} seconds'.format(datetime.now() - start_time))
        if save:

            start_time = datetime.now()
            logger.debug('save starting')
            self._save_with_django(cor, anime_list)

            logger.info('save finished, done in {} seconds'.format(datetime.now() - start_time))

        return cor, anime_list

    def _save_with_django(self, sm, index, created=datetime.now()):
        start_time = datetime.now()
        Similarity.objects.all().delete()
        logger.info(f'truncating table in {datetime.now() - start_time} seconds')
        sims = []
        no_saved = 0
        start_time = datetime.now()
        coo = coo_matrix(sm)
        csr = coo.tocsr()

        logger.info(f'instantiation of coo_matrix in {datetime.now() - start_time} seconds')
        logger.info(f'{coo.count_nonzero()} similarities to save')
        xs, ys = coo.nonzero()
        for x, y in zip(xs, ys):

            if x == y:
                continue

            sim = csr[x, y]

            if sim < self.min_sim:
                continue

            if len(sims) == 500000:
                Similarity.objects.bulk_create(sims)
                sims = []
                logger.debug(f"{no_saved} saved in {datetime.now() - start_time}")

            new_similarity = Similarity(
                source=index[x],
                target=index[y],
                created=created,
                similarity=sim
            )
            no_saved += 1
            sims.append(new_similarity)
        Similarity.objects.bulk_create(sims)
        logger.info('{} Similarity items saved, done in {} seconds'.format(no_saved, datetime.now() - start_time))


def main():
    logger.info("Calculation of item similarity")

    all_ratings = load_all_ratings()
    ItemSimilarityMatrixBuilder(min_overlap=10, min_sim=0.0).build(all_ratings, save=False)


def normalize(x):
    x = x.astype(float)
    x_sum = x.sum()
    x_num = x.astype(bool).sum()
    x_mean = x_sum / x_num

    if x_num == 1 or x.std() == 0:
        return 0.0
    return (x - x_mean) / (x.max() - x.min())


def load_all_ratings(min_ratings=1):
    columns = ['user_id', 'anime_id', 'rating']

    ratings_data = UserRating.objects.all().values(*columns)

    ratings = pd.DataFrame.from_records(ratings_data, columns=columns)
    user_count = ratings[['user_id', 'anime_id']].groupby('user_id').count()
    user_count = user_count.reset_index()
    user_ids = user_count[user_count['anime_id'] > min_ratings]['user_id']
    ratings = ratings[ratings['user_id'].isin(user_ids)]
    ratings['rating'] = ratings['rating'].astype(float)
    return ratings


if __name__ == '__main__':
    main()
