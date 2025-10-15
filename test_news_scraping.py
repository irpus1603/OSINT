import os
import django

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'osint_dashboard.settings')
django.setup()

from scraper.tasks import scrape_news_source
from scraper.models import Source

def test_news_scraping():
    """Test news scraping task"""
    print("Testing news scraping...")
    
    # Get the first news source
    news_source = Source.objects.filter(source_type='news', is_active=True).first()
    
    if news_source:
        print(f"Scraping source: {news_source.name}")
        print(f"Source URL: {news_source.url}")
        
        # Run the scraping task synchronously for testing
        try:
            result = scrape_news_source(news_source.id)
            print(f"Scraping result: {result}")
        except Exception as e:
            print(f"Error during scraping: {e}")
    else:
        print("No active news sources found")

if __name__ == '__main__':
    test_news_scraping()