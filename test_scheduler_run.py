import os
import django

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'osint_dashboard.settings')
django.setup()

from scheduler.views import run_task
from scheduler.models import CrawlTask, CrawlLog
from scraper.models import Source, Article
from django.http import JsonResponse
from django.utils import timezone

def test_scheduler_run():
    """Test scheduler run task functionality"""
    print("Testing scheduler run task...")
    
    # Get BBC crawl task
    bbc_task = CrawlTask.objects.filter(source__name='BBC World').first()
    
    if bbc_task:
        print("Task: {}".format(bbc_task.name))
        print("Source: {}".format(bbc_task.source.name))
        print("Source type: {}".format(bbc_task.source.source_type))
        
        # Count existing articles
        articles_before = Article.objects.filter(source=bbc_task.source).count()
        print("Articles before: {}".format(articles_before))
        
        # Count existing logs
        logs_before = CrawlLog.objects.filter(task=bbc_task).count()
        print("Logs before: {}".format(logs_before))
        
        # Simulate running the task
        print("Simulating task run...")
        
        try:
            # Create a mock request object
            class MockRequest:
                method = 'POST'
                META = {}
                COOKIES = {}
            
            # Run the task
            # Note: We can't directly call run_task because it requires a real Django request
            # Instead, let's directly call the scraper task
            from scraper.tasks import scrape_news_source, scrape_social_media_source
            
            if bbc_task.source.source_type == 'news':
                result = scrape_news_source(bbc_task.source.id)
                print("Scraping result: {}".format(result))
            elif bbc_task.source.source_type == 'social':
                result = scrape_social_media_source(bbc_task.source.id)
                print("Scraping result: {}".format(result))
                
            # Update task status
            bbc_task.last_run = timezone.now()
            bbc_task.status = 'completed'
            bbc_task.save()
            print("Task status updated")
            
            # Count articles after
            articles_after = Article.objects.filter(source=bbc_task.source).count()
            print("Articles after: {}".format(articles_after))
            print("Net articles created: {}".format(articles_after - articles_before))
            
            # Count logs after
            logs_after = CrawlLog.objects.filter(task=bbc_task).count()
            print("Logs after: {}".format(logs_after))
            
        except Exception as e:
            print("Error running task: {}".format(e))
            import traceback
            traceback.print_exc()
    else:
        print("BBC crawl task not found")

if __name__ == '__main__':
    test_scheduler_run()