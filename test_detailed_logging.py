import os
import django

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'osint_dashboard.settings')
django.setup()

import logging
logging.basicConfig(level=logging.INFO)

from scraper.tasks import scrape_news_source
from scraper.models import Source

def test_detailed_logging():
    \"\"\"Test detailed logging during scraping\"\"\"
    print(\"Testing detailed logging...\")
    
    # Get Reuters source
    reuters_source = Source.objects.filter(name='Reuters', is_active=True).first()
    
    if reuters_source:
        print(f\"Testing scrape_news_source for: {reuters_source.name}\")
        print(f\"Source URL: {reuters_source.url}\")
        
        # Run the scraping task with detailed logging
        result = scrape_news_source(reuters_source.id)
        print(f\"\\nFinal result: {result}\")
    else:
        print(\"Reuters source not found\")

if __name__ == '__main__':
    test_detailed_logging()