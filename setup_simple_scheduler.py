#!/usr/bin/env python
"""
Setup simplified crawler scheduler for man guarding services
"""
import os
import django
from datetime import datetime, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'osint_dashboard.settings')
django.setup()

from scheduler.models import CrawlTask, CrawlLog
from scraper.models import Source, Keyword
from django.utils import timezone

def setup_scheduler():
    """Setup simplified crawler scheduler"""

    print("=" * 70)
    print("SETTING UP SIMPLIFIED CRAWLER SCHEDULER")
    print("=" * 70)

    # Step 1: Clean up old tasks
    print("\n1. Cleaning up old crawl tasks...")
    old_tasks = CrawlTask.objects.all()
    deleted_count = old_tasks.delete()[0]
    print(f"   ✓ Deleted {deleted_count} old tasks")

    # Step 2: Clean up old logs (keep last 100)
    print("\n2. Cleaning up old crawl logs (keeping last 100)...")
    logs = CrawlLog.objects.all().order_by('-created_at')
    if logs.count() > 100:
        logs_to_keep = list(logs[:100].values_list('id', flat=True))
        deleted_logs = CrawlLog.objects.exclude(id__in=logs_to_keep).delete()[0]
        print(f"   ✓ Deleted {deleted_logs} old logs")
    else:
        print(f"   ✓ Keeping all {logs.count()} logs")

    # Step 3: Get active sources
    print("\n3. Loading active sources...")
    news_sources = Source.objects.filter(is_active=True, source_type='news')
    social_sources = Source.objects.filter(is_active=True, source_type='social')

    print(f"   ✓ Found {news_sources.count()} news sources")
    print(f"   ✓ Found {social_sources.count()} social media sources")

    # Step 4: Get active keywords
    print("\n4. Loading active keywords...")
    keywords = Keyword.objects.filter(is_active=True)
    print(f"   ✓ Found {keywords.count()} active keywords")

    # Step 5: Create simplified crawl tasks
    print("\n5. Creating simplified crawl tasks...")

    # Task 1: Hourly news crawl (all Indonesian news sources)
    task1 = CrawlTask.objects.create(
        name='Crawl Berita Indonesia (Setiap Jam)',
        source=news_sources.first(),  # We'll crawl all, but need one as FK
        frequency='hourly',
        is_active=True,
        next_run=timezone.now() + timedelta(hours=1),
        status='pending'
    )
    task1.keywords.set(keywords)
    print(f"   ✓ Created: {task1.name}")

    # Task 2: Daily comprehensive crawl
    task2 = CrawlTask.objects.create(
        name='Crawl Harian Menyeluruh',
        source=news_sources.first(),
        frequency='daily',
        is_active=True,
        next_run=timezone.now() + timedelta(days=1),
        status='pending'
    )
    task2.keywords.set(keywords)
    print(f"   ✓ Created: {task2.name}")

    # Task 3: Social media monitoring (if configured)
    if social_sources.exists():
        task3 = CrawlTask.objects.create(
            name='Monitoring Media Sosial (Harian)',
            source=social_sources.first(),
            frequency='daily',
            is_active=False,  # Disabled by default until Twitter API is configured
            next_run=timezone.now() + timedelta(days=1),
            status='pending'
        )
        task3.keywords.set(keywords)
        print(f"   ✓ Created: {task3.name} (disabled - configure Twitter API first)")

    # Summary
    print("\n6. Summary:")
    total_tasks = CrawlTask.objects.filter(is_active=True).count()
    print(f"   - Total active tasks: {total_tasks}")
    print(f"   - Total keywords monitored: {keywords.count()}")
    print(f"   - Total news sources: {news_sources.count()}")

    print("\n" + "=" * 70)
    print("SCHEDULER SETUP COMPLETE")
    print("=" * 70)

    print("\nActive Crawl Tasks:")
    for task in CrawlTask.objects.filter(is_active=True):
        next_run_str = task.next_run.strftime('%Y-%m-%d %H:%M') if task.next_run else 'Not scheduled'
        print(f"  • {task.name}")
        print(f"    Frequency: {task.frequency}")
        print(f"    Next run: {next_run_str}")
        print()

    print("How to use:")
    print("  1. Start services: ./start_server.sh")
    print("  2. Access scheduler: http://127.0.0.1:8000/scheduler/")
    print("  3. Click 'Run Task' to manually trigger crawling")
    print("  4. Celery Beat will run tasks automatically based on schedule")

    print("\nNotes:")
    print("  • Hourly crawl: Runs every hour for fresh news")
    print("  • Daily crawl: Comprehensive crawl once per day")
    print("  • Social media: Disabled until Twitter API is configured in .env")

if __name__ == '__main__':
    setup_scheduler()
