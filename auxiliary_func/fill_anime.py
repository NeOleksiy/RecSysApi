import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "RecSystem.settings")

import django

django.setup()
from productApi.models import *
import pandas as pd
from tqdm import tqdm

anime = pd.read_csv('../anime.csv')
rating = pd.read_csv('../rating.csv')

anime['genre'] = anime['genre'].fillna('None')
anime['rating'] = anime['rating'].fillna(0)

products = [
    Anime(
        anime_id=anime.iloc[row]['anime_id'],
        name=anime.iloc[row]['name'],
        # genre=anime.iloc[row]['genre'],
        type=anime.iloc[row]['type'],
        episodes=(anime.iloc[row]['episodes'] if anime.iloc[row]['episodes'] != 'Unknown' else anime['episodes'][
            anime['episodes'] != 'Unknown'].astype(int).median()),
        rating=(anime.iloc[row]['rating'] if anime.iloc[row]['rating'] != 'nan' else 0.00),
        members=anime.iloc[row]['members']
    )
    for row in anime.index
]

for i, g in tqdm(enumerate(products)):
    g.save()
    genres = anime.iloc[i]['genre'].split(',')
    genres_id = []
    for new_genre in genres:
        Genre.objects.get_or_create(genre=new_genre)
        genres_id.append(Genre.objects.get(genre=new_genre).pk)

    g.genre.set(genres_id)

print(Anime.objects.filter(anime_id=1))
