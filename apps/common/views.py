# Create your views here.
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.serializers import Serializer


class HealthView(GenericAPIView):
    authentication_classes = ()
    permission_classes = (AllowAny,)
    serializer_class = Serializer

    def get(self, request):
        return Response({
            'live': True,
        })


class ProtectedTestView(GenericAPIView):
    serializer_class = Serializer

    def get(self, request):
        return Response({
            'live': True,
        })
