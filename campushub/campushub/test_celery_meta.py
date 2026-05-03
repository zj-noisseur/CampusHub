import sys
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'campushub.settings')
sys.path.append('/home/bruce/dev/projects/CampusHub-linux/campushub')
django.setup()

from celery.result import AsyncResult
from django_celery_results.models import TaskResult

for task in TaskResult.objects.filter(status='PROGRESS'):
    print("PROGRESS DB:", task.task_id, task.meta, task.result)
    res = AsyncResult(task.task_id)
    print("PROGRESS Async:", task.task_id, res.state, res.info)

