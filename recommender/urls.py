from django.urls import path
from recommender.views import CollaborateFilteringRecs, ContentBasedRecommender, FWLS, Popularity

urlpatterns = [
    path('collaborate_filtering/', CollaborateFilteringRecs.as_view(),
         name='Online Collaborate Filtering'),
    path('content_based/', ContentBasedRecommender.as_view(), name='Content Based Recommends'),
    path('fwls/', FWLS.as_view(), name='FWLS'),
    path('popular/', Popularity.as_view({'get': 'list'}), name='Popular content')
]
