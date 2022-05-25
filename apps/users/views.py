# Create your views here.
from django.contrib.auth.models import User
from drf_util.decorators import serialize_decorator
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from apps.users.models import CustomUser
from apps.users.serializers import UserSerializer, FullNameUserSerializer


class RegisterUserView(GenericAPIView):
    serializer_class = UserSerializer

    permission_classes = (AllowAny,)
    authentication_classes = ()

    @serialize_decorator(UserSerializer)
    def post(self, request):
        validated_data = request.serializer.validated_data

        user = CustomUser.objects.create(
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            email=validated_data['email'],
            is_superuser=True,
            is_staff=True
        )
        user.set_password(validated_data['password'])
        user.save()

        return Response(UserSerializer(user).data)


class UserListView(GenericAPIView):
    serializer_class = FullNameUserSerializer

    permission_classes = (AllowAny,)
    authentication_classes = ()

    def get(self, request):
        users = CustomUser.objects.all()

        return Response(FullNameUserSerializer(users, many=True).data)
