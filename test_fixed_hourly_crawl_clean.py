import os
import django

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'osint_dashboard.settings')
django.setup()

from scraper.tasks import scrape_news_source
from scraper.models import Source, Article

def test_fixed_hourly_crawl():
    # Test the fixed hourly news crawl
    print("Testing fixed hourly news crawl...")
    
    # Get the "fixed" Reuters source (now pointing to BBC)
    reuters_source = Source.objects.filter(name='Reuters').first()
    
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
        
        # Count articles before
        articles_before = Article.objects.filter(source=reuters_source).count()
        print("Articles before: {}".format(articles_before))
        
        # Run the scraping task
        print("\nRunning scraping task...")
        result = scrape_news_source(reuters_source.id)
        print("Result: {}".format(result))
        
        # Count articles after
        articles_after = Article.objects.filter(source=reuters_source).count()
        print("Articles after: {}".format(articles_after))
        print("Net articles created: {}".format(articles_after - articles_before))
        
        # Show recent articles
        if articles_after > articles_before:
            recent_articles = Article.objects.filter(source=reuters_source).order_by('-scraped_at')[:3]
            print("\nNew articles created:")
            for article in recent_articles:
                print("  - {} ({})".format(article.title, article.scraped_at))
    else:
        print("Reuters source not found")

if __name__ == '__main__':
    test_fixed_hourly_crawl()