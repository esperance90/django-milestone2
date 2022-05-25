# Create your views here.
from drf_util.decorators import serialize_decorator
from rest_framework import serializers
from rest_framework.generics import GenericAPIView, get_object_or_404
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from apps.tasks.models import Task
from apps.tasks.serializers import TaskSerializer, TaskIdTittleSerializer, TaskIdSerializer, TaskAllDetailsSerializer


class AddNewTaskView(GenericAPIView):
    serializer_class = TaskSerializer

    @serialize_decorator(TaskSerializer)
    def post(self, request):
        validated_data = request.serializer.validated_data

        task = Task.objects.create(
            user=self.request.user,
            description=validated_data['description'],
            title=validated_data['title'],
            status=validated_data['status']
        )

        return Response(TaskIdSerializer(task).data)


class TaskListView(GenericAPIView):
    serializer_class = TaskIdTittleSerializer

    def get(self, request):
        tasks = Task.objects.all()

        return Response(TaskIdTittleSerializer(tasks, many=True).data)


class TaskListCurrentUserView(GenericAPIView):
    serializer_class = TaskIdTittleSerializer

    def get(self, request):
        user = self.request.user
        tasks = Task.objects.filter(user=user)

        return Response(TaskIdTittleSerializer(tasks, many=True).data)


class TaskItemView(GenericAPIView):
    serializer_class = TaskAllDetailsSerializer

    permission_classes = (AllowAny,)
    authentication_classes = ()

    def get(self, request, pk):
        task = get_object_or_404(Task.objects.filter(pk=pk))

        return Response(TaskAllDetailsSerializer(task).data)
