import os
import django

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'osint_dashboard.settings')
django.setup()

from scheduler.models import CrawlTask
from scraper.models import Source

def check_task_sources():
    # Check sources for crawl tasks
    print("Checking sources for crawl tasks...")
    
    tasks = CrawlTask.objects.all()
    for task in tasks:
        print("\nTask: {}".format(task.name))
        print("  Source: {} ({})".format(task.source.name, task.source.source_type))
        print("  Source URL: {}".format(task.source.url))
        print("  Source Active: {}".format(task.source.is_active))
        
        # Test URL accessibility
        import requests
        try:
            response = requests.head(task.source.url, timeout=10)
            print("  URL Status: {} {}".format(response.status_code, "OK" if response.status_code == 200 else "Error"))
        except Exception as e:
            print("  URL Status: Error - {}".format(str(e)))

if __name__ == '__main__':
    check_task_sources()