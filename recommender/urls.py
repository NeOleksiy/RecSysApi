from django.urls import path
from recommender.views import Similar_users, OnlineCollaborateFiltering

urlpatterns = [
    path('similar_recs/<int:user_id>/<str:sim_method>/', Similar_users.as_view(), name='similar_users'),
    path('collaborate_filtering/<int:user_id>/', OnlineCollaborateFiltering.as_view(),
         name='online_collaborate_filtering')
]
