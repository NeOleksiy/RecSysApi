import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "RecSystem.settings")

import django

django.setup()
from users.models import *
from productApi.models import *
import pandas as pd
from tqdm import tqdm

rating = pd.read_csv('../rating.csv')
rating = rating[rating["rating"] != -1]
rating.drop(rating[rating['anime_id'] == 30913].index, axis=0, inplace=True)
# users = [
#     User(
#         user_id=int(row),
#         username='User'+str(row)
#     )
#     for row in rating['user_id'].unique()
# ]
#
# User.objects.bulk_create(users)

# products = [
#     UserRating(
#         user_id=User.objects.get(user_id=rating.iloc[row]['user_id']),
#         anime_id=Anime.objects.get(anime_id=rating.iloc[row]['anime_id']),
#         rating=rating.iloc[row]['rating'],
#     )
#     for row in tqdm(rating.index)
# ]
for row in tqdm(rating.index):
    try:
        u = UserRating(
            user_id=User.objects.get(user_id=rating.iloc[row]['user_id']),
            anime_id=Anime.objects.get(anime_id=rating.iloc[row]['anime_id']),
            rating=rating.iloc[row]['rating'],
        )
        u.save()
    except:
        continue

# UserRating.objects.bulk_create(products)


print(UserRating.objects.first())
