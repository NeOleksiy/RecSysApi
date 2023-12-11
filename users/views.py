from rest_framework import authentication
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.generics import ListAPIView, CreateAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from productApi.models import UserRating
from users.models import User
from rest_framework import exceptions
from rest_framework import generics
from .serializers import UserSerializer, UserRatingSerializer


class ExampleView(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        content = {
            'user': str(request.user),  # `django.contrib.auth.User` instance.
            'auth': str(request.auth),  # None
        }
        return Response(content)


class ExampleAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        username = request.META.get('HTTP_X_USERNAME')
        if not username:
            return None

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise exceptions.AuthenticationFailed('No such user')

        return (user, None)


# views.py


class UserRegistrationView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]


class UserWatchList(ListAPIView):
    serializer_class = UserRatingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return UserRating.objects.filter(user_id=user.user_id)


class UserAddWatchList(CreateAPIView):
    serializer_class = UserRatingSerializer
    permission_classes = [IsAuthenticated]
    queryset = UserRating.objects.all()


