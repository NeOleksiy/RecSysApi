from django.urls import path
from recommender.views import Similar_users

urlpatterns = [
    path('similar_recs/<int:user_id>/<str:sim_method>/', Similar_users.as_view(), name='similar_users')
]