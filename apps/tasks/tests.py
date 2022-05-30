from itertools import count

from django.test import TestCase
from rest_framework.reverse import reverse
from rest_framework.test import APIClient
from rest_framework.utils import json

from apps.tasks.models import StatusTypes, Task
from apps.tasks.serializers import TaskAllDetailsSerializer, CommentSerializer
from apps.users.models import CustomUser

task_id = count(start=1)
comment_id = count(start=1)


def get_id(entity_id):
    return next(entity_id)


def get_task(user_id, status):
    new_id = get_id(task_id)
    task = {
        "id": new_id,
        "user": user_id,
        "title": "New title" + str(new_id),
        "description": "New description" + str(new_id),
        "status": status
    }
    return task


def get_new_task(user_id):
    new_id = get_id(task_id)
    task = {
        "id": new_id,
        "user": user_id,
        "title": "New title" + str(new_id),
        "description": "New description" + str(new_id),
        "status": StatusTypes.CREATED
    }
    return task


def get_new_comment(task):
    new_id = get_id(comment_id)
    comment = {
        "id": new_id,
        "text": "dummy comment" + str(new_id),
        "task": task
    }
    return comment


class TestTasks(TestCase):
    fixtures = ['initial_data']

    def setUp(self) -> None:
        self.client = APIClient()
        # check data in fixture json file
        self.test_user = CustomUser.objects.get(email="gudumacnadea@gmail.com")
        self.tasks = Task.objects.all()
        self.client.force_authenticate(self.test_user)

    def test_create(self):
        task = get_new_task(self.test_user.id)
        response = self.client.post(reverse('new_task'), data=task)
        self.assertEqual(response.status_code, 200)

    def test_get(self):
        response = self.client.get(reverse('list_tasks'))
        self.assertEqual(response.status_code, 200)

    def test_complete_task(self):
        task = get_new_task(self.test_user.id)
        response = self.client.post(reverse('new_task'), data=task)
        self.assertEqual(response.status_code, 200)

        response = self.client.patch(reverse('complete_task', kwargs={'pk': task['id']}))
        task = Task.objects.get(id=task['id'])
        self.assertEqual(task.status, StatusTypes.COMPLETED)
        self.assertEqual(response.status_code, 200)

    def test_get_my_tasks(self):
        response = self.client.get(reverse('show_my_tasks'))
        self.assertEqual(response.status_code, 200)
        tasks = TaskAllDetailsSerializer(self.tasks, many=True).data
        # my_tasks = list(filter(lambda task: task['user'] == self.test_user.id,
        #                        tasks))
        tasks_response = json.loads(response.content)
        # print(tasks_response)
        #
        # print(my_tasks)
        # self.assertEqual(tasks_response, my_tasks)
        self.assertEqual(len(tasks_response), 2)

    def test_add_task_comment(self):
        task = get_new_task(self.test_user.id)
        response = self.client.post(reverse('new_task'), data=task)
        self.assertEqual(response.status_code, 200)

        response = self.client.post(reverse('add_comment', kwargs={'pk': task['id']}),
                                    data=get_new_comment(task['id']))

        self.assertEqual(response.status_code, 200)

    def test_list_comments(self):
        task = get_new_task(self.test_user.id)
        response = self.client.post(reverse('new_task'), data=task)
        self.assertEqual(response.status_code, 200)

        comment = get_new_comment(task['id'])
        response = self.client.post(reverse('add_comment', kwargs={'pk': task['id']}), format='json', data=comment)
        self.assertEqual(response.status_code, 200)

        comment2 = get_new_comment(task['id'])
        response = self.client.post(reverse('add_comment', kwargs={'pk': task['id']}), format='json', data=comment2)
        self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse('list_comments', kwargs={'pk': task['id']}))
        self.assertEqual(response.status_code, 200)
        #comments = json.loads(response.content)
        print(json.loads(response.content))
        comments = CommentSerializer(json.loads(response.content), many=True).data
        print(comments)
        #self.assertEqual(comments, 2)



