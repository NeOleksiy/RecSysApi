from django.urls import path
from recommender.views import Similar_users, CollaborateFilteringRecs, ContentBasedRecommender, FWLS

urlpatterns = [
    path('similar_recs/<int:user_id>/<str:sim_method>/', Similar_users.as_view(), name='Similar Users'),
    path('collaborate_filtering/<int:user_id>/', CollaborateFilteringRecs.as_view(),
         name='Online Collaborate Filtering'),
    path('content_based/<int:user_id>/', ContentBasedRecommender.as_view(), name='Content Based Recommends'),
    path('fwls/<int:user_id>/', FWLS.as_view(), name='FWLS')
]
