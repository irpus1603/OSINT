import os
import django

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'osint_dashboard.settings')
django.setup()

from scraper.tasks import scrape_news_source
from scraper.models import Source, Article

def test_fresh_article_creation():
    # Test fresh article creation by temporarily removing recent articles
    print("Testing fresh article creation...")
    
    # Get the "fixed" Reuters source (now pointing to BBC)
    reuters_source = Source.objects.filter(name='Reuters').first()
    
    if reuters_source:
        print("Source: {}".format(reuters_source.name))
        print("URL: {}".format(reuters_source.url))
        
        # Count existing articles
        articles_before = Article.objects.filter(source=reuters_source).count()
        print("Existing articles from this source: {}".format(articles_before))
        
        # Show some recent articles
        recent_articles = Article.objects.filter(source=reuters_source).order_by('-scraped_at')[:3]
        print("\nRecent articles:")
        for article in recent_articles:
            print("  - {} ({})".format(article.title, article.scraped_at))
        
        # Run the scraping task
        print("\nRunning scraping task...")
        result = scrape_news_source(reuters_source.id)
        print("Result: {}".format(result))
        
        # Count articles after
        articles_after = Article.objects.filter(source=reuters_source).count()
        print("Articles after: {}".format(articles_after))
        print("Net articles created: {}".format(articles_after - articles_before))
        
        # Show any new articles
        if articles_after > articles_before:
            new_articles = Article.objects.filter(source=reuters_source).order_by('-scraped_at')[:3]
            print("\nNew articles created:")
            for article in new_articles:
                print("  - {} ({})".format(article.title, article.scraped_at))
        else:
            print("\nNo new articles created (existing articles already in database)")
    else:
        print("Reuters source not found")

if __name__ == '__main__':
    test_fresh_article_creation()