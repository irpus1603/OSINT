from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from .models import CrawlTask, CrawlLog
from scraper.tasks import scrape_news_source, scrape_social_media_source, run_scheduled_scraping
import logging

# Set up logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Ensure we have a console handler for immediate output
if not logger.handlers:
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

@shared_task
def execute_scheduled_crawl_tasks():
    """
    Execute crawl tasks based on their schedule
    """
    logger.info("=== Starting scheduled crawl task execution ===")
    now = timezone.now()
    
    # Get all active tasks that should run now
    tasks_to_run = CrawlTask.objects.filter(
        is_active=True,
        next_run__lte=now
    )
    
    logger.info(f"Found {tasks_to_run.count()} tasks due for execution")
    
    results = []
    for task in tasks_to_run:
        logger.info(f"Processing crawl task: {task.name} (ID: {task.id}) for source: {task.source.name}")
        logger.info(f"Task details - Frequency: {task.frequency}, Last run: {task.last_run}, Next run: {task.next_run}")
        try:
            logger.info(f"Creating log entry for task: {task.name}")
            # Create log entry
            log = CrawlLog.objects.create(
                task=task,
                started_at=now,
                status='running'
            )
            
            # Run the appropriate scraping task
            if 'Batch Crawl' in task.name or 'All News Sources' in task.name:
                logger.info(f"🚀 Dispatching BATCH CRAWL for ALL NEWS SOURCES")
                result = run_scheduled_scraping.delay()
                logger.info(f"Batch crawling task dispatched with Celery task ID: {result.id}")
                from scraper.models import Source
                active_news_count = Source.objects.filter(source_type='news', is_active=True).count()
                logger.info(f"This will process ALL {active_news_count} active news sources")
            elif task.source.source_type == 'news':
                logger.info(f"Dispatching single news scraping task for source: {task.source.name} (ID: {task.source.id})")
                result = scrape_news_source.delay(task.source.id)
                logger.info(f"Single news scraping task dispatched with Celery task ID: {result.id}")
            elif task.source.source_type == 'social':
                logger.info(f"Dispatching social media scraping task for source: {task.source.name} (ID: {task.source.id})")
                result = scrape_social_media_source.delay(task.source.id)
                logger.info(f"Social media scraping task dispatched with Celery task ID: {result.id}")
            else:
                raise ValueError(f"Unsupported source type: {task.source.source_type}")
            
            # Update task schedule
            task.last_run = now
            task.next_run = calculate_next_run(task.frequency, now)
            task.status = 'completed'
            task.save()
            logger.info(f"Updated task schedule - Next run: {task.next_run}")
            
            # Update log
            log.status = 'success'
            log.finished_at = timezone.now()
            log.items_scraped = 0  # This would need to be updated by the task
            log.save()
            
            results.append(f"Task {task.name} executed successfully")
            logger.info(f"✓ Task {task.name} completed successfully")
            
        except Exception as e:
            logger.error(f"✗ Task {task.name} failed with error: {str(e)}")
            # Update task status
            task.status = 'failed'
            task.save()
            
            # Update log
            if 'log' in locals():
                log.status = 'failed'
                log.finished_at = timezone.now()
                log.error_message = str(e)
                log.save()
            
            results.append(f"Task {task.name} failed: {str(e)}")
    
    final_message = f"Executed {len(results)} tasks: " + "; ".join(results)
    logger.info(f"=== Scheduled crawl task execution completed: {final_message} ===")
    return final_message

def calculate_next_run(frequency, last_run):
    """
    Calculate next run time based on frequency
    """
    if frequency == 'hourly':
        return last_run + timedelta(hours=1)
    elif frequency == 'daily':
        return last_run + timedelta(days=1)
    elif frequency == 'weekly':
        return last_run + timedelta(weeks=1)
    else:
        # Default to daily
        return last_run + timedelta(days=1)