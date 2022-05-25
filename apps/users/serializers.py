from django.contrib.auth.models import User
from rest_framework import serializers

from apps.tasks.serializers import TaskSerializer
from apps.users.models import CustomUser


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    tasks = TaskSerializer(many=True, read_only=True)

    class Meta:
        model = CustomUser
        fields = ("first_name", "last_name", "email", "password", "tasks")


class FullNameUserSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    def get_full_name(self, obj):
        return '{} {}'.format(obj.first_name, obj.last_name)

    class Meta:
        model = CustomUser
        fields = ("id", "full_name")
