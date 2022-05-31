from django.core.management.base import BaseCommand

from apps.tasks.helpers import generate_random_timelog
from apps.tasks.models import Task

class Command(BaseCommand):
    help = 'Create random timelog'

    def add_arguments(self, parser):
        parser.add_argument('total', type=int, help='Indicates the number of timelog to be created')

    def handle(self, *args, **kwargs):
        total = kwargs['total']
        tasks = Task.objects.all()
        timelogs_per_task = int(total / len(tasks))
        for task in tasks:
            for i in range(timelogs_per_task):
                generate_random_timelog(task)
