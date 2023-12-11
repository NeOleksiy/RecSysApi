from django.urls import path, include
from rest_framework.authtoken import views
from .views import UserRegistrationView, UserWatchList, UserAddWatchList

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='user-registration'),
    path('auth/', include('rest_framework.urls')),
    path('watch_list/', UserWatchList.as_view(), name='User Watch List'),
    path('add_watch_list/', UserAddWatchList.as_view(), name='User add anime in watch List'),
    # path('api-token-auth/', views.obtain_auth_token)
]
