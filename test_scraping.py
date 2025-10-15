#!/usr/bin/env python
import os
import django

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'osint_dashboard.settings')
django.setup()

from scraper.services import ScraperService

def test_scraping():
    """Test the scraping functionality"""
    print("Testing scraping functionality...")
    
    # Show statistics
    stats = ScraperService.get_scraping_stats()
    print(f"Current statistics:")
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    print("\nStarting scraping of all sources...")
    results = ScraperService.scrape_all_sources()
    
    print("\nScraping results:")
    for result in results:
        if result['status'] == 'success':
            print(f"  ✓ {result['source']}: {result['result']}")
        else:
            print(f"  ✗ {result['source']}: {result['result']}")

if __name__ == '__main__':
    test_scraping()