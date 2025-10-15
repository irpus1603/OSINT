import os
import django

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'osint_dashboard.settings')
django.setup()

import logging
from scraper.tasks import scrape_news_source
from scraper.models import Source

def test_logging():
    """Test that logging works correctly"""
    print("Testing logging functionality...")
    
    # Set up logging to see output
    logging.basicConfig(level=logging.INFO)
    
    # Get a source to test
    source = Source.objects.filter(is_active=True, source_type='news').first()
    
    if source:
        print(f"Testing scrape_news_source for: {source.name}")
        print(f"Source URL: {source.url}")
        
        # Run the scraping task
        result = scrape_news_source(source.id)
        print(f"Result: {result}")
    else:
        print("No active news sources found")

if __name__ == '__main__':
    test_logging()