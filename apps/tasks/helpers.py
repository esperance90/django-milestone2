import enum
from datetime import timedelta
from smtplib import SMTPException

from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone


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
