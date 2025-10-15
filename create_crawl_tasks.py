import os
import django
from datetime import datetime, timedelta

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'osint_dashboard.settings')
django.setup()

from scheduler.models import CrawlTask
from scraper.models import Source, Keyword

def create_sample_crawl_tasks():
    """
    Create sample crawl tasks for demonstration
    """
    # Get all sources and keywords
    sources = Source.objects.all()
    keywords = Keyword.objects.all()[:5]  # Just use first 5 keywords for demo
    
    # Create crawl tasks
    tasks_data = [
        {
            'name': 'Hourly News Crawl',
            'source': sources.filter(source_type='news').first(),
            'frequency': 'hourly',
            'is_active': True
        },
        {
            'name': 'Daily Social Media Crawl',
            'source': sources.filter(source_type='social').first(),
            'frequency': 'daily',
            'is_active': True
        },
        {
            'name': 'Weekly Security News Crawl',
            'source': sources.filter(source_type='news').last(),
            'frequency': 'weekly',
            'is_active': True
        }
    ]
    
    for task_data in tasks_data:
        # Check if task already exists
        task, created = CrawlTask.objects.get_or_create(
            name=task_data['name'],
            defaults=task_data
        )
        
        if created:
            # Add keywords to the task
            task.keywords.set(keywords)
            # Set next run time
            if task.frequency == 'hourly':
                task.next_run = datetime.now() + timedelta(hours=1)
            elif task.frequency == 'daily':
                task.next_run = datetime.now() + timedelta(days=1)
            elif task.frequency == 'weekly':
                task.next_run = datetime.now() + timedelta(weeks=1)
            
            task.save()
            print(f"Created crawl task: {task.name}")
        else:
            print(f"Crawl task already exists: {task.name}")

if __name__ == '__main__':
    print("Creating sample crawl tasks...")
    create_sample_crawl_tasks()
    print("Sample crawl tasks created!")