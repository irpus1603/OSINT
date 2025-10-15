import os
import django

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'osint_dashboard.settings')
django.setup()

from scraper.tasks import scrape_news_source
from scraper.models import Source

def test_hourly_news_crawl():
    """Test the actual hourly news crawl task"""
    print("Testing hourly news crawl...")
    
    # Get Reuters source (the one used by Hourly News Crawl task)
    reuters_source = Source.objects.filter(name='Reuters', is_active=True).first()
    
    if reuters_source:
        print("Source: {}".format(reuters_source.name))
        print("URL: {}".format(reuters_source.url))
        
        # Test URL accessibility
        import requests
        try:
            response = requests.head(reuters_source.url, timeout=10)
            print("URL Status: {} {}".format(response.status_code, "OK" if response.status_code == 200 else "Error"))
        except Exception as e:
            print("URL Status: Error - {}".format(str(e)))
        
        # Run the scraping task
        print("\nRunning scraping task...")
        result = scrape_news_source(reuters_source.id)
        print("Result: {}".format(result))
    else:
        print("Reuters source not found")

if __name__ == '__main__':
    test_hourly_news_crawl()