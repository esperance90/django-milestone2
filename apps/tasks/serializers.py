from enumchoicefield import EnumChoiceField
from rest_framework import serializers

from apps.tasks.models import Task, StatusTypes, Comment, TimeLog


class TaskAllDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ("id", "title", "description", "status", "user")


class TaskSerializer(serializers.ModelSerializer):
    status = EnumChoiceField(enum_class=StatusTypes)

    class Meta:
        model = Task
        fields = ("title", "description", "status",)


class TaskUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ("user",)


class TaskIdTittleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ("id", "title")


class TaskIdSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ["id", ]


class TaskStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ["status", ]


class CommentIdSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ["id", ]


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ["text", "task"]


class CommentTextSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ["text", ]


class TimeLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = TimeLog
        # read_only_fields = ("start_time",)
        fields = ["start_time", "stop_time", "duration"]


class TimeLogManualSerializer(serializers.ModelSerializer):
    class Meta:
        model = TimeLog
        # read_only_fields = ("start_time",)
        fields = ["start_time", "duration"]


class TimeLogStartSerializer(serializers.ModelSerializer):
    class Meta:
        model = TimeLog
        read_only_fields = ("task", "start_time",)
        fields = ["task", "start_time"]


class TimeLogStopSerializer(serializers.ModelSerializer):
    class Meta:
        model = TimeLog
        fields = ["stop_time"]
