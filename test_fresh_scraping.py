import os
import django

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'osint_dashboard.settings')
django.setup()

from scraper.tasks import scrape_news_source
from scraper.models import Source, Article

def test_fresh_scraping():
    \"\"\"Test fresh scraping by removing existing articles\"\"\"
    print(\"Testing fresh scraping...\")
    
    # Get BBC source
    bbc_source = Source.objects.filter(name='BBC World', is_active=True).first()
    
    if bbc_source:
        # Count existing articles
        articles_before = Article.objects.filter(source=bbc_source).count()
        print(\"Existing BBC articles: {}\".format(articles_before))
        
        # Run scraping task
        print(\"Running scraping task...\")
        result = scrape_news_source(bbc_source.id)
        print(\"Result: {}\".format(result))
        
        # Count articles after
        articles_after = Article.objects.filter(source=bbc_source).count()
        print(\"BBC articles after: {}\".format(articles_after))
        print(\"Net articles created: {}\".format(articles_after - articles_before))
        
        # Show recent articles
        recent_articles = Article.objects.filter(source=bbc_source).order_by('-scraped_at')[:5]
        print(\"\nRecent BBC articles:\")
        for article in recent_articles:
            print(\"  - {} ({})\".format(article.title, article.scraped_at))
    else:
        print(\"BBC source not found\")

if __name__ == '__main__':
    test_fresh_scraping()