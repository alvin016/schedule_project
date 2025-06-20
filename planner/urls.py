from django.urls import path
from . import views

urlpatterns = [
    path('', views.daily_schedule, name='daily_schedule'),
    path('ajax/schedule-task/', views.ajax_schedule_task, name='ajax_schedule_task'),
    path('ajax/delete-scheduled-task/', views.ajax_delete_scheduled_task, name='ajax_delete_scheduled_task'),


]
