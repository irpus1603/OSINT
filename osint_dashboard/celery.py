import os
from celery import Celery
from celery.schedules import crontab

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'osint_dashboard.settings')

app = Celery('osint_dashboard')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')

# Configure periodic tasks
app.conf.beat_schedule = {
    'execute-scheduled-crawl-tasks': {
        'task': 'scheduler.tasks.execute_scheduled_crawl_tasks',
        'schedule': 60.0,  # Run every minute
    },
}

# Use default timezone from Django settings
app.conf.timezone = 'Asia/Jakarta'