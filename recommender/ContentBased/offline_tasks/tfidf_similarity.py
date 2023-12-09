import os
import pandas as pd
import logging
import scipy as sp
from tqdm import tqdm
from sklearn.metrics.pairwise import cosine_similarity
from scipy.sparse import coo_matrix
from datetime import datetime
from sklearn.feature_extraction.text import TfidfVectorizer
import json
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "RecSystem.settings")

import django

django.setup()

from productApi.models import UserRating, Genre, Anime
from recommender.models import TfIdfMatrix
from RecSystem import settings

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.DEBUG)
logger = logging.getLogger('TFIDF simialarity calculator')


class Tf_IdfSimilarityBuilder:
    def __init__(self, min_overlap=10, min_sim=0.3):
        self.min_overlap = min_overlap
        self.min_sim = min_sim

    @staticmethod
    def load_anime_genres():
        genres = []
        for anime in Anime.objects.all():
            genres.append(' '.join([i.genre for i in anime.genre.all()]))
        return genres

    def build(self, genres, save=True):

        logger.info("Calculating similarities {} anime".format(len(genres)))
        start_time = datetime.now()

        logger.info("Creating TF-IDF similarity matrix")
        tfidf = TfidfVectorizer(stop_words="english")
        tfidf_matrix = tfidf.fit_transform(genres)
        tfidf.get_feature_names_out()

        cosine_sm = cosine_similarity(tfidf_matrix, dense_output=False)
        coo = coo_matrix(cosine_sm)
        coo = coo.multiply(coo > self.min_sim)
        print(coo.count_nonzero())
        if save:
            start_time = datetime.now()
            logger.debug('save starting')
            self._save_with_django(coo)

            logger.info('save finished, done in {} seconds'.format(datetime.now() - start_time))

    def _save_with_django(self, sm, created=datetime.now()):
        start_time = datetime.now()
        sims = []
        TfIdfMatrix.objects.all().delete()
        counter = 0
        for i, j, tfidf in tqdm(zip(*sp.sparse.find(sm))):
            if len(sims) == 500000:
                TfIdfMatrix.objects.bulk_create(sims)
                sims = []
                logger.debug(f"{counter} sims saved in {datetime.now() - start_time}")
            sims.append(TfIdfMatrix(row_id=i, col_id=j, tfidf_sim=tfidf))
            counter += 1
        TfIdfMatrix.objects.bulk_create(sims)


def main():
    logger.info("Calculation of item TF-IDF")
    genres = Tf_IdfSimilarityBuilder.load_anime_genres()
    Tf_IdfSimilarityBuilder().build(genres, save=True)


if __name__ == '__main__':
    main()
