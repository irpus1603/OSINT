#!/usr/bin/env python
"""
Trigger crawl tasks immediately
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'osint_dashboard.settings')
django.setup()

from scheduler.models import CrawlTask
from django.utils import timezone

print("=" * 60)
print("TRIGGERING IMMEDIATE CRAWL")
print("=" * 60)

# Get active tasks
tasks = CrawlTask.objects.filter(is_active=True)

print(f"\nFound {tasks.count()} active tasks\n")

for task in tasks:
    old_next_run = task.next_run
    task.next_run = timezone.now()
    task.save()

    print(f"✓ {task.name}")
    print(f"  Old next run: {old_next_run}")
    print(f"  New next run: {task.next_run} (NOW)")
    print()

print("=" * 60)
print("DONE - Tasks will run in the next minute")
print("=" * 60)

print("\nMonitor progress:")
print("  tail -f scraper.log")
print("  tail -f celery_worker.log")
