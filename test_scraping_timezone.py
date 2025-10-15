import os
import django
from django.utils import timezone

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'osint_dashboard.settings')
django.setup()

from scraper.models import Article, Post, Source
from scraper.tasks import scrape_news_source, scrape_social_media_source

def test_scraping_with_timezone():
    """Test scraping tasks with timezone awareness"""
    print("Testing scraping with timezone awareness...")
    
    # Get active sources
    news_source = Source.objects.filter(source_type='news', is_active=True).first()
    social_source = Source.objects.filter(source_type='social', is_active=True).first()
    
    if news_source:
        print(f"Testing news scraping for source: {news_source.name}")
        try:
            result = scrape_news_source(news_source.id)
            print(f"News scraping result: {result}")
        except Exception as e:
            print(f"Error in news scraping: {e}")
    
    if social_source:
        print(f"Testing social media scraping for source: {social_source.name}")
        try:
            result = scrape_social_media_source(social_source.id)
            print(f"Social media scraping result: {result}")
        except Exception as e:
            print(f"Error in social media scraping: {e}")
    
    print("Scraping test completed!")

if __name__ == '__main__':
    test_scraping_with_timezone()