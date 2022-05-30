from django.urls import path

from apps.tasks.views import AddNewTaskView, TaskListView, TaskItemView, TaskListCurrentUserView, TaskCompletedListView, \
    TaskCompleteView, TaskAssignView, AddTaskCommentView, ListTaskCommentsView, TaskSearchListView, StartTaskView, \
    StopTaskView, AddTimelogView, GetTimelogView, LastMonthTopTimelogView, LastMonthTimelogView

urlpatterns = [
    path('', TaskListView.as_view(), name='list_tasks'),
    path('task', AddNewTaskView.as_view(), name='new_task'),
    path('search', TaskSearchListView.as_view(), name='task_search'),
    path('<int:pk>', TaskItemView.as_view(), name='task_item'),
    path('<int:pk>/complete', TaskCompleteView.as_view(), name='complete_task'),
    path('<int:pk>/assign', TaskAssignView.as_view(), name='assign_task'),
    path('<int:pk>/comment', AddTaskCommentView.as_view(), name='add_comment'),
    path('<int:pk>/comments', ListTaskCommentsView.as_view(), name='list_comments'),
    path('<int:pk>/start', StartTaskView.as_view(), name='start_task'),
    path('<int:pk>/stop', StopTaskView.as_view(), name='stop_task'),
    path('<int:pk>/timelog', AddTimelogView.as_view(), name='add_timelog'),
    path('timelog/last-month', LastMonthTimelogView.as_view(), name='get_last_month_timelog'),
    path('timelog/top20', LastMonthTopTimelogView.as_view(), name='get_top_last_month_timelog'),
    path('<int:pk>/timelog/all', GetTimelogView.as_view(), name='get_timelog'),
    path('current-user', TaskListCurrentUserView.as_view(), name='show_my_tasks'),
    path('completed', TaskCompletedListView.as_view(), name='get_completed_tasks'),
]
