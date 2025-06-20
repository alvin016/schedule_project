from django.contrib import admin
from .models import Task, ScheduledTask

admin.site.register(Task)
admin.site.register(ScheduledTask)
