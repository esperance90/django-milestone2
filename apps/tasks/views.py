# Create your views here.
from drf_util.decorators import serialize_decorator
from drf_yasg.utils import swagger_auto_schema, no_body
from rest_framework.generics import get_object_or_404, DestroyAPIView, \
    UpdateAPIView, ListAPIView, CreateAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from apps.tasks.models import Task, StatusTypes, Comment
from apps.tasks.serializers import TaskSerializer, TaskIdTittleSerializer, TaskIdSerializer, TaskAllDetailsSerializer, \
    CommentSerializer, TaskUserSerializer, CommentIdSerializer, CommentTextSerializer


class AddNewTaskView(CreateAPIView):
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


class AddTaskCommentView(CreateAPIView):
    serializer_class = CommentTextSerializer

    @serialize_decorator(CommentTextSerializer)
    def post(self, request, pk):
        validated_data = request.serializer.validated_data

        comment = Comment.objects.create(
            text=validated_data['text'],
            task_id=pk
        )

        return Response(CommentIdSerializer(comment).data)


class ListTaskCommentsView(ListAPIView):
    serializer_class = CommentSerializer

    def get_queryset(self):
        task_id = self.kwargs.get('pk', 0)
        return Comment.objects.filter(task_id=task_id)


class TaskListView(ListAPIView):
    serializer_class = TaskIdTittleSerializer
    queryset = Task.objects.all()


class TaskCompletedListView(ListAPIView):
    serializer_class = TaskIdTittleSerializer
    queryset = Task.objects.filter(status=StatusTypes.COMPLETED)


class TaskListCurrentUserView(ListAPIView):
    serializer_class = TaskIdTittleSerializer

    def get_queryset(self):
        return Task.objects.filter(user=self.request.user)


class TaskItemView(ListAPIView, DestroyAPIView):
    serializer_class = TaskAllDetailsSerializer
    queryset = Task.objects.all()

    permission_classes = (AllowAny,)
    authentication_classes = ()

    def get(self, request, pk):
        task = get_object_or_404(Task.objects.filter(pk=pk))

        return Response(TaskAllDetailsSerializer(task).data)


class TaskCompleteView(UpdateAPIView):
    @swagger_auto_schema(request_body=no_body)
    def patch(self, request, *args, **kwargs):
        task = self.get_object()

        task.status = StatusTypes.COMPLETED
        task.save(update_fields=['status'])
        return Response({'complete': True})


class TaskAssignView(UpdateAPIView):
    serializer_class = TaskUserSerializer

    @serialize_decorator(TaskUserSerializer)
    def patch(self, request, pk):
        validated_data = request.serializer.validated_data

        task = Task.objects.get(pk=pk)
        task.user = validated_data['user']
        task.save(update_fields=['user'])
        return Response({'assigned': True})
