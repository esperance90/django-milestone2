# Create your views here.
import enum
from smtplib import SMTPException

from django.conf import settings
from django.core.mail import send_mail
from drf_util.decorators import serialize_decorator
from drf_yasg.utils import swagger_auto_schema, no_body
from rest_framework import filters
from rest_framework.generics import get_object_or_404, DestroyAPIView, \
    UpdateAPIView, ListAPIView, CreateAPIView, GenericAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.serializers import Serializer

from apps.tasks.models import Task, StatusTypes, Comment
from apps.tasks.serializers import TaskSerializer, TaskIdTittleSerializer, TaskIdSerializer, TaskAllDetailsSerializer, \
    CommentSerializer, TaskUserSerializer, CommentIdSerializer, CommentTextSerializer


class NotificationTypes(enum.Enum):
    TASK_ASSIGN = 1
    TASK_COMMENT = 2
    TASK_COMPLETE = 3


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
    queryset = Task.objects.all()

    @serialize_decorator(CommentTextSerializer)
    def post(self, request, pk):
        validated_data = request.serializer.validated_data

        comment = Comment.objects.create(
            text=validated_data['text'],
            task_id=pk
        )

        task = Task.objects.get(pk=pk)
        current_user = self.request.user

        if task.user_id == current_user.id:
            send_notification(NotificationTypes.TASK_COMMENT, task)
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
    serializer_class = Serializer
    queryset = Task.objects.exclude(status=StatusTypes.COMPLETED)

    @swagger_auto_schema(request_body=no_body)
    def patch(self, request, pk):
        task = self.get_object()

        task.status = StatusTypes.COMPLETED
        task.save(update_fields=['status'])

        send_notification(NotificationTypes.TASK_COMPLETE, task)

        return Response({'complete': True})


class TaskAssignView(GenericAPIView):
    serializer_class = TaskUserSerializer

    def get_queryset(self):
        user = self.request.serializer.validated_data['user']
        return Task.objects.exclude(user_id=user.id)

    @serialize_decorator(TaskUserSerializer)
    def patch(self, request, *args, **kwargs):
        validated_data = request.serializer.validated_data

        task = self.get_object()
        task.user = validated_data['user']
        task.save(update_fields=['user'])

        if task.user_id == self.request.user.id:
            send_notification(NotificationTypes.TASK_ASSIGN, task)
        return Response({'assigned': True})


class TaskSearchListView(ListAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['title']


def send_notification(notification_type, task):
    subject = f'New activity on task: {task.title}!'
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [task.user.email, ]
    msg_generic = f'Hi {task.user.first_name} {task.user.last_name}!'

    if notification_type == NotificationTypes.TASK_ASSIGN:
        message = f'{msg_generic} Task id:{task.id} was assigned to you!'
    elif notification_type == NotificationTypes.TASK_COMMENT:
        message = f'{msg_generic} New comment on task id:{task.id}!'
    elif notification_type == NotificationTypes.TASK_COMPLETE:
        message = f'{msg_generic} Task id:{task.id} is completed!'
    try:
        send_mail(subject, message, email_from, recipient_list)
    except SMTPException as e:
        print('E-mail sending failed', e)
