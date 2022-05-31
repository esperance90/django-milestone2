# Create your views here.
from django.db.models import Sum
from django.utils import timezone
from drf_util.decorators import serialize_decorator
from drf_yasg.utils import swagger_auto_schema, no_body
from rest_framework import filters
from rest_framework.generics import get_object_or_404, DestroyAPIView, \
    UpdateAPIView, ListAPIView, CreateAPIView, GenericAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.serializers import Serializer

from apps.tasks.helpers import get_start_month_datetime, send_notification, NotificationTypes
from apps.tasks.models import Task, StatusTypes, Comment, TimeLog
from apps.tasks.serializers import TaskSerializer, TaskIdTittleSerializer, TaskIdSerializer, TaskAllDetailsSerializer, \
    CommentSerializer, TaskUserSerializer, CommentIdSerializer, CommentTextSerializer, TimeLogSerializer, \
    TimeLogStartSerializer, TimeLogManualSerializer, TimeLogStopSerializer


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
        return Comment.objects.filter(task_id=self.kwargs['pk'])


class TaskListView(ListAPIView):
    serializer_class = TaskIdTittleSerializer
    queryset = Task.objects.all()

    def get(self, request, *args, **kwargs):
        start_month_datetime = get_start_month_datetime()

        tasks = Task.objects.filter(
            timelog__start_time__gt=start_month_datetime) \
            .values('id', 'title').annotate(total_time=Sum('timelog__duration'))
        return Response(tasks)


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
        return Task.objects.exclude(user=user)

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


class StartTaskView(CreateAPIView):
    serializer_class = Serializer

    def get_queryset(self):
        return TimeLog.objects.filter(task_id=self.kwargs['pk'], stop_time__isnull=True)

    @serialize_decorator(TimeLogStartSerializer)
    @swagger_auto_schema(request_body=no_body)
    def post(self, request, pk):

        task_id = self.kwargs['pk']
        # check if the task is owned by current user
        tasks_by_current_user = Task.objects.filter(id=task_id, user=self.request.user)
        if not tasks_by_current_user.exists():
            return Response({"created": False, "cause": "Task is not owned by current user!"})

        # check that the task cannot be started multiple times without stopping
        if self.get_queryset().exists():
            return Response({"started": False, "cause": "Already Started. Please stop first."})

        current_time = timezone.now()
        TimeLog.objects.create(
            start_time=current_time,
            task_id=pk
        )

        return Response({"started": True})


class StopTaskView(UpdateAPIView):
    serializer_class = Serializer
    queryset = TimeLog.objects.all()

    @serialize_decorator(TimeLogStopSerializer)
    @swagger_auto_schema(request_body=no_body)
    def patch(self, request, pk):
        timelog = TimeLog.objects.filter(task__user_id=self.request.user, task_id=pk,
                                         stop_time__isnull=True).first()
        if not timelog:
            return Response({"stopped": False, "cause": "Already stopped or not found!"})

        timelog.stop_time = timezone.now()
        timelog.duration = timelog.stop_time - timelog.start_time
        timelog.save(update_fields=['stop_time', 'duration'])

        return Response({"stopped": True})


class AddTimelogView(CreateAPIView):
    serializer_class = TimeLogManualSerializer
    queryset = TimeLog.objects.all()

    @serialize_decorator(TimeLogManualSerializer)
    def post(self, request, pk):
        validated_data = request.serializer.validated_data

        task = self.kwargs['pk']
        current_user = self.request.user
        qs = Task.objects.filter(user=current_user, id=task, user_id=self.request.user.id)
        if not qs.exists():
            return Response({"created": False, "cause": "Task is not owned by current user!"})

        current_time = timezone.now()
        timelog = TimeLog.objects.create(
            start_time=current_time,
            duration=validated_data['duration'] * 60,
            stop_time=current_time + validated_data['duration'] * 60,
            task_id=pk
        )

        return Response(TimeLogSerializer(timelog).data)


class LastMonthTimelogView(ListAPIView):
    serializer_class = TimeLogSerializer
    queryset = TimeLog.objects.all()

    def get(self, request, *args, **kwargs):
        start_month_datetime = get_start_month_datetime()
        total_time = TimeLog.objects.filter(task__user_id=self.request.user.id, start_time__gt=start_month_datetime) \
            .aggregate(total_time=Sum('duration'))
        return Response({"total_time": total_time['total_time'].seconds})


class LastMonthTopTimelogView(ListAPIView):
    serializer_class = TaskSerializer
    queryset = Task.objects.all()

    def get(self, request, *args, **kwargs):
        start_month_datetime = get_start_month_datetime()
        tasks = Task.objects.filter(user=self.request.user, timelog__start_time__gt=start_month_datetime) \
                    .values('id', 'title').annotate(total_time=Sum('timelog__duration')) \
                    .order_by('-total_time')[:20]
        return Response(tasks)


class GetTimelogView(ListAPIView):
    serializer_class = TimeLogSerializer

    def get_queryset(self):
        task_id = self.kwargs.get('pk', 0)
        return TimeLog.objects.filter(task_id=task_id)
