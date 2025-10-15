import os
import django

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'osint_dashboard.settings')
django.setup()

from scheduler.models import CrawlTask, CrawlLog
from django.utils import timezone

def test_task_cancellation():
    """Test task cancellation functionality"""
    print("Testing task cancellation...")
    
    # Check current running tasks
    running_tasks = CrawlTask.objects.filter(status='running')
    print(f"Currently running tasks: {running_tasks.count()}")
    
    for task in running_tasks:
        print(f"- {task.name}: {task.status}")
        
        # Create a test log entry for this task
        log = CrawlLog.objects.create(
            task=task,
            started_at=timezone.now(),
            status='running'
        )
        print(f"  Created test log entry: {log.id}")
    
    print("Task cancellation test setup completed!")

if __name__ == '__main__':
    test_task_cancellation()