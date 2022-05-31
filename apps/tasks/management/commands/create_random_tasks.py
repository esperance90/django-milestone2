from django.core.management.base import BaseCommand

from apps.tasks.helpers import get_new_task
from apps.users.models import CustomUser


class Command(BaseCommand):
    help = 'Create random tasks'

    def add_arguments(self, parser):
        parser.add_argument('total', type=int, help='Indicates the number of tasks to be created')

    def handle(self, *args, **kwargs):
        total = kwargs['total']
        user = CustomUser.objects.get(email="gudumacnadea@gmail.com")
        for i in range(total):
            get_new_task(user)