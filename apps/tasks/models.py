from datetime import timedelta

from django.db import models
from django.utils import timezone

from apps.users.models import CustomUser


# Create your models here.

class StatusTypes(models.TextChoices):
    CREATED = "created"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class Task(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    title = models.CharField(max_length=200, unique=True)
    description = models.TextField()
    status = models.CharField(max_length=30, choices=StatusTypes.choices, default=StatusTypes.CREATED)


class Comment(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    text = models.TextField()


class TimeLog(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    start_time = models.DateTimeField(default=timezone.now)
    stop_time = models.DateTimeField(blank=True, null=True)
    duration = models.DurationField(default=timedelta())
