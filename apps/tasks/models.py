from django.db import models

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
