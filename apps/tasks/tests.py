from datetime import timedelta
from itertools import count
from random import randrange

from django.test import TestCase
from django.utils import timezone
from rest_framework.reverse import reverse
from rest_framework.test import APIClient
from rest_framework.utils import json

from apps.tasks.helpers import get_start_month_datetime
from apps.tasks.models import StatusTypes, Task, Comment, TimeLog
from apps.users.models import CustomUser

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


class TestTasks(TestCase):
    fixtures = ['initial_data']

    def setUp(self) -> None:
        self.client = APIClient()
        # check data in fixture json file
        self.test_user = CustomUser.objects.get(email="gudumacnadea@gmail.com")
        self.test_user2 = CustomUser.objects.get(email="test@gmail.com")
        self.client.force_authenticate(self.test_user)

    def test_create(self):
        new_id = get_id(task_id)
        task = {'id': new_id,
                'user': self.test_user.id,
                'title': "New title" + str(new_id),
                'description': "New description" + str(new_id),
                'status': StatusTypes.CREATED}

        response = self.client.post(reverse('new_task'), data=task,
                                    format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Task.objects.count(), 1)

    def test_get(self):
        response = self.client.get(reverse('list_tasks'))
        self.assertEqual(response.status_code, 200)

    def test_complete_task(self):
        test_task = get_new_task(self.test_user)

        response = self.client.patch(reverse('complete_task', kwargs={'pk': test_task.id}))
        test_task.refresh_from_db()

        self.assertEqual(test_task.status, StatusTypes.COMPLETED)
        self.assertEqual(response.status_code, 200)

    def test_get_my_tasks(self):
        get_new_task(self.test_user)
        get_new_task(self.test_user2)
        response = self.client.get(reverse('show_my_tasks'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Task.objects.filter(user=self.test_user2).count(), 1)

    def test_add_task_comment(self):
        task = get_new_task(self.test_user)
        new_id = get_id(comment_id)
        comment = {'id': new_id,
                   'text': "dummy comment" + str(new_id),
                   'task': task.id}

        response = self.client.post(reverse('add_comment', kwargs={'pk': task.id}),
                                    data=comment, format='json')

        self.assertEqual(response.status_code, 200)
        comment = Comment.objects.get(id=comment['id'])
        self.assertIsNotNone(comment)

    def test_list_comments(self):
        task = get_new_task(self.test_user)
        get_new_comment(task)
        get_new_comment(task)

        response = self.client.get(reverse('list_comments', kwargs={'pk': task.id}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Comment.objects.count(), 2)

    def test_get_completed(self):
        get_new_task(self.test_user)
        get_task(self.test_user, StatusTypes.CREATED)
        task3 = get_task(self.test_user, StatusTypes.COMPLETED)

        completed_tasks = [task3]
        response = self.client.get(reverse('get_completed_tasks'))

        tasks = json.loads(response.content)
        self.assertEqual(len(tasks), len(completed_tasks))

    def test_task_assign(self):
        test_task = get_new_task(self.test_user)
        data = {'user': self.test_user2.id}

        response = self.client.patch(reverse('assign_task', kwargs={'pk': test_task.id}), data=data,
                                     format='json')

        test_task.refresh_from_db()
        self.assertEqual(test_task.user, self.test_user2)
        self.assertEqual(response.status_code, 200)

    def test_task_start(self):
        test_task = get_new_task(self.test_user)

        timelog = {
            'start_time': get_start_month_datetime(),
            'task': test_task.id
        }
        response = self.client.post(reverse('start_task', kwargs={'pk': test_task.id}), data=timelog,
                                    format='json')
        timelog = TimeLog.objects.get()
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(timelog)
        self.assertEqual(timelog.task.id, test_task.id)
        self.assertIsNone(timelog.stop_time)

    def test_task_stop(self):
        test_task = get_new_task(self.test_user)
        timelog = get_new_timelog(test_task, timezone.now() - timedelta(days=1))
        response = self.client.patch(reverse('stop_task', kwargs={'pk': test_task.id}))
        self.assertEqual(response.status_code, 200)
        timelog.refresh_from_db()
        self.assertIsNotNone(timelog.stop_time)
        self.assertIsNotNone(timelog.duration)

    def test_add_timelog(self):
        test_task = get_new_task(self.test_user)
        timelog = {
            'start_time': timezone.now(),
            'duration': 120,
            'task': test_task.id
        }

        response = self.client.post(reverse('add_timelog', kwargs={'pk': test_task.id}), data=timelog,
                                    format='json')
        timelog = TimeLog.objects.get()
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(timelog)
        self.assertEqual(timelog.task.id, test_task.id)

    def test_last_month_timelog(self):
        task = get_new_task(self.test_user)
        # log 2 hours
        get_timelog(task, timezone.now(), 120)
        # log 4 hours
        get_timelog(task, timezone.now() - timedelta(1), 240)
        response = self.client.get(reverse('get_last_month_timelog'))
        total_time = json.loads(response.content)
        # 6 hours in seconds = 6*60*60
        self.assertIsNotNone(total_time['total_time'])
        self.assertEqual(total_time['total_time'], 6 * 60 * 60)

    def test_top20_timelog(self):
        get_new_task(self.test_user2)

        tasks = []
        for x in range(25):
            task = get_new_task(self.test_user)
            tasks.append(task)

        for task in tasks:
            generate_random_timelog(task)

        response = self.client.get(reverse('get_top_last_month_timelog'))
        top_tasks = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(top_tasks), 20)

    def test_all_timelog(self):
        task = get_new_task(self.test_user)

        for x in range(10):
            generate_random_timelog(task)

        response = self.client.get(reverse('get_timelog', kwargs={'pk': task.id}))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(TimeLog.objects.count(), 10)

    def test_task_search(self):
        get_new_task(self.test_user)
        get_new_task(self.test_user)
        response = self.client.get(reverse('task_search'), {'search': 'new'})
        response_json_list=json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response_json_list), 2)

    def test_task_view(self):
        task = get_new_task(self.test_user)
        get_new_task(self.test_user)
        response = self.client.get(reverse('task_item', kwargs={'pk': task.id}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(task.title, json.loads(response.content)['title'])
