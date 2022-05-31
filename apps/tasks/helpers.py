import enum
from datetime import timedelta
from itertools import count
from random import randrange
from smtplib import SMTPException

from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone

from apps.tasks.models import TimeLog, Comment, Task, StatusTypes


def send_notification(notification_type, task):
    subject = f'New activity on task: {task.title}!'
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [task.user.email, ]
    generic_message = f'Hi {task.user.first_name} {task.user.last_name}!'

    notifications = {
        NotificationTypes.TASK_ASSIGN: f'{generic_message} Task id:{task.id} was assigned to you!',
        NotificationTypes.TASK_COMMENT: f'{generic_message} New comment on task id:{task.id}!',
        NotificationTypes.TASK_COMPLETE: f'{generic_message} Task id:{task.id} is completed!'
    }

    message = (lambda custom_msg: custom_msg)(notifications.get(notification_type))

    try:
        send_mail(subject, message, email_from, recipient_list)
    except SMTPException as e:
        print('E-mail sending failed', e)


def get_start_month_datetime():
    current_day = timezone.now().day
    start_month_datetime = timezone.now() - timedelta(days=current_day)
    return start_month_datetime


class NotificationTypes(enum.Enum):
    TASK_ASSIGN = 1
    TASK_COMMENT = 2
    TASK_COMPLETE = 3


task_id = count(start=1)
comment_id = count(start=1)
timelog_id = count(start=1)


def get_id(entity_id):
    return next(entity_id)


def get_task(user, status):
    new_id = get_id(task_id)
    task = Task.objects.create(id=new_id,
                               user=user,
                               title="New title" + str(new_id),
                               description="New description" + str(new_id),
                               status=status)
    return task


def get_new_task(user):
    new_id = get_id(task_id)
    task = Task.objects.create(id=new_id,
                               user=user,
                               title="New title" + str(new_id),
                               description="New description" + str(new_id),
                               status=StatusTypes.CREATED)
    return task


def get_new_comment(task):
    new_id = get_id(comment_id)
    comment = Comment.objects.create(id=new_id,
                                     text="dummy comment" + str(new_id),
                                     task=task)
    return comment


def get_new_timelog(task, start_time):
    new_id = get_id(timelog_id)
    timelog = TimeLog.objects.create(id=new_id, task=task, start_time=start_time)
    return timelog


def get_timelog(task, start_time, duration):
    new_id = get_id(timelog_id)
    stop_time = start_time + timedelta(minutes=duration)
    timelog = TimeLog.objects.create(id=new_id, task=task, start_time=start_time,
                                     duration=timedelta(minutes=duration),
                                     stop_time=stop_time)
    return timelog


def generate_random_timelog(task):
    random_duration = randrange(1, 10) * 60
    random_start = timezone.now() - timedelta(randrange(1, 7))
    return get_timelog(task, random_start, random_duration)

