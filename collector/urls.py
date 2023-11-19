from django.urls import path
from collector.views import Logging

urlpatterns = [
    path('logging/', Logging.as_view(), name='logging events'),
]
