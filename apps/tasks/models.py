from django.db import models

from enumchoicefield import ChoiceEnum, EnumChoiceField

from apps.users.models import CustomUser


# Create your models here.

class StatusTypes(ChoiceEnum):
    created = "created"
    in_progress = "in_progress"
    completed = "completed"


class Task(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    title = models.CharField(max_length=200, unique=True)
    description = models.TextField()
    status = EnumChoiceField(enum_class=StatusTypes, default=StatusTypes.created)
