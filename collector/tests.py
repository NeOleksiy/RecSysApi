from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from django.urls import include, path, reverse
from rest_framework.test import APITestCase, URLPatternsTestCase
from collector.models import Logs
from django.contrib.auth.hashers import make_password


class LogsTests(APITestCase, URLPatternsTestCase):
    urlpatterns = [
        path('collect/', include('collector.urls'))
    ]

    def test_create_logs(self):
        User = get_user_model()
        user = User.objects.create_superuser(user_id=100000, username='testuser', password='testpassword')
        # client = APIClient()
        self.client.login(username='testuser', password='testpassword')
        self.client.force_authenticate(user=user)
        url = reverse('logging events')
        data = {
            "content_id": 3,
            "event": "open site",
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
