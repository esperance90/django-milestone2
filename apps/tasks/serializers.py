from rest_framework import serializers
from apps.tasks.models import Task

class TaskAllDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ("id", "title", "description", "status", "user")

class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ("title", "description", "status",)


class TaskIdTittleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ("id", "title")


class TaskIdSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ["id", ]

