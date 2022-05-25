from django.urls import path

from apps.tasks.views import AddNewTaskView, TaskListView, TaskItemView, TaskListCurrentUserView

urlpatterns = [
    path('task/', AddNewTaskView.as_view(), name='new_task'),
    path('current-user/', TaskListCurrentUserView.as_view(), name='show_tasks'),
    path('task/<int:pk>/', TaskItemView.as_view(), name='blog_item'),
    path('', TaskListView.as_view(), name='new_task'),
]
