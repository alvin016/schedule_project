from django.shortcuts import render, redirect
from datetime import time, datetime
from .models import Task, ScheduledTask
from django.utils.timezone import now
from .forms import TaskForm
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json


def daily_schedule(request):
    today = now().date()
    tasks = Task.objects.all()
    scheduled_tasks = ScheduledTask.objects.filter(date=today)

    time_slots = [f"{hour:02d}:00" for hour in range(6, 24)]  # 06:00~23:00
    
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('daily_schedule')
    else:
        form = TaskForm()

    # 建立時間對應已排任務的 dict
    scheduled_map = {}
    for st in scheduled_tasks:
        slot_key = st.start_time.strftime("%H:%M")
        scheduled_map.setdefault(slot_key, []).append(st)

    return render(request, 'planner/daily_schedule.html', {
        'tasks': tasks,
        'task_form': form,
        'scheduled_map': scheduled_map,
        'time_slots': time_slots,
        'today': today,
    })
@csrf_exempt
def ajax_schedule_task(request):
    if request.method == 'POST':
        data = json.loads(request.body)

        task_id = data.get('task_id')
        time_str = data.get('time')   # e.g. "06:00"
        date_str = data.get('date')   # e.g. "2025-06-20"

        try:
            task = Task.objects.get(id=task_id)
            start_time = datetime.strptime(time_str, "%H:%M").time()
            end_hour = (start_time.hour + 1) if start_time.hour < 23 else 23
            end_time = datetime.strptime(f"{end_hour:02d}:00", "%H:%M").time()
            date = datetime.strptime(date_str, "%Y-%m-%d").date()
            
            exists = ScheduledTask.objects.filter(task=task, date=date).exists()
            if exists:
                return JsonResponse({'status': 'duplicate', 'message': '該任務已排入今天的其他時段'})


            ScheduledTask.objects.create(
                task=task,
                date=date,
                start_time=start_time,
                end_time=end_time,
            )
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})

    return JsonResponse({'status': 'invalid'})


@csrf_exempt
def ajax_delete_scheduled_task(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        task_id = data.get('task_id')
        date_str = data.get('date')
        time_str = data.get('time')

        try:
            date = datetime.strptime(date_str, "%Y-%m-%d").date()
            start_time = datetime.strptime(time_str, "%H:%M").time()

            scheduled = ScheduledTask.objects.get(
                task_id=task_id,
                date=date,
                start_time=start_time
            )
            scheduled.delete()
            return JsonResponse({'status': 'deleted'})
        except ScheduledTask.DoesNotExist:
            return JsonResponse({'status': 'not_found'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})

    return JsonResponse({'status': 'invalid'})
