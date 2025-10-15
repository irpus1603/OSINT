import os
import django

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'osint_dashboard.settings')
django.setup()

from scheduler.models import CrawlTask, CrawlLog
from scraper.models import Source

def check_crawl_tasks():
    \"\"\"Check all crawl tasks\"\"\"
    print(\"Checking crawl tasks...\")
    
    tasks = CrawlTask.objects.all()
    print(\"Total tasks: {}\".format(tasks.count()))
    
    for task in tasks:
        print(\"\\nTask: {}\".format(task.name))
        print(\"  Source: {} ({})\".format(task.source.name, task.source.source_type))
        print(\"  Frequency: {}\".format(task.frequency))
        print(\"  Active: {}\".format(task.is_active))
        print(\"  Status: {}\".format(task.status))
        print(\"  Last run: {}\".format(task.last_run))
        print(\"  Next run: {}\".format(task.next_run))
        
    # Check logs
    logs = CrawlLog.objects.all().order_by('-started_at')[:5]
    print(\"\\nRecent logs:\")
    for log in logs:
        print(\"  {} - {} - {}\".format(log.task.name, log.status, log.started_at))

if __name__ == '__main__':
    check_crawl_tasks()