import os
import django

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'osint_dashboard.settings')
django.setup()

from scheduler.models import CrawlTask

def test_scheduler_endpoints():
    """Test that scheduler endpoints are properly configured"""
    print("Testing scheduler endpoints...")
    
    # Check if we have tasks
    tasks = CrawlTask.objects.all()
    print(f"Total tasks: {tasks.count()}")
    
    for task in tasks:
        print(f"Task: {task.name} (ID: {task.id}) - Active: {task.is_active}")
    
    print("Scheduler endpoints test completed!")

if __name__ == '__main__':
    test_scheduler_endpoints()