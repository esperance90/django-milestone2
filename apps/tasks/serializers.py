from enumchoicefield import EnumChoiceField
from rest_framework import serializers

from apps.tasks.models import Task, StatusTypes, Comment


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
