from django.urls import path
from . import views

app_name = 'scheduler'

urlpatterns = [
    path('', views.scheduler_dashboard, name='dashboard'),
    path('run-task/<int:task_id>/', views.run_task, name='run_task'),
    path('run-scheduled/', views.run_scheduled_tasks, name='run_scheduled'),
    path('update-schedule/<int:task_id>/', views.update_task_schedule, name='update_schedule'),
    path('toggle-status/<int:task_id>/', views.toggle_task_status, name='toggle_status'),
    path('reset-schedule/<int:task_id>/', views.reset_task_schedule, name='reset_schedule'),
    path('stop-all/', views.stop_all_tasks, name='stop_all'),
    path('start-all/', views.start_all_tasks, name='start_all'),
    path('stop-celery/', views.stop_celery_processes, name='stop_celery'),
    path('start-celery/', views.start_celery_processes, name='start_celery'),
    path('celery-status/', views.get_celery_status, name='celery_status'),
    path('cancel-task/<int:task_id>/', views.cancel_running_task, name='cancel_task'),
]