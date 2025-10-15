#!/usr/bin/env python
"""
Real-time monitoring script for OSINT Dashboard scraping tasks
"""

import os
import django
import logging
import sys
import time
from datetime import datetime

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'osint_dashboard.settings')
django.setup()

from scraper.tasks import scrape_news_source, scrape_social_media_source
from scraper.models import Source
from scheduler.models import CrawlTask

def monitor_scraping():
    """Monitor scraping tasks in real-time"""
    print("=" * 60)
    print("OSINT Dashboard - Real-time Scraping Monitor")
    print("=" * 60)
    print("This script will monitor scraping tasks and show detailed logs.")
    print("Press Ctrl+C to stop monitoring.")
    print("=" * 60)
    
    # Set up logging to show in console
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Show available sources
    print("\nAvailable Sources:")
    sources = Source.objects.filter(is_active=True)
    for source in sources:
        print(f"  {source.id}. {source.name} ({source.source_type}) - {source.url}")
    
    # Show available tasks
    print("\nAvailable Crawl Tasks:")
    tasks = CrawlTask.objects.filter(is_active=True)
    for task in tasks:
        print(f"  {task.id}. {task.name} - {task.source.name} ({task.frequency})")
    
    print("\n" + "=" * 60)
    print("Monitoring will start automatically...")
    print("Run specific scraping tasks to see detailed logs.")
    print("=" * 60)
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\nMonitoring stopped.")
        sys.exit(0)

def test_single_source(source_id):
    """Test scraping for a single source with detailed logging"""
    print(f"\nTesting source ID: {source_id}")
    
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    try:
        source = Source.objects.get(id=source_id, is_active=True)
        print(f"\nStarting scrape for: {source.name}")
        print(f"Source type: {source.source_type}")
        print(f"Source URL: {source.url}")
        print("-" * 50)
        
        if source.source_type == 'news':
            result = scrape_news_source(source.id)
        elif source.source_type == 'social':
            result = scrape_social_media_source(source.id)
        else:
            print(f"Unsupported source type: {source.source_type}")
            return
            
        print("-" * 50)
        print(f"Final result: {result}")
        
    except Source.DoesNotExist:
        print(f"Source with ID {source_id} not found or inactive")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    if len(sys.argv) > 1:
        # Test specific source
        try:
            source_id = int(sys.argv[1])
            test_single_source(source_id)
        except ValueError:
            print("Invalid source ID. Please provide a number.")
    else:
        # Monitor mode
        monitor_scraping()