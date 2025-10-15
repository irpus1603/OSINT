import os
import django
from datetime import datetime
from django.utils import timezone

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'osint_dashboard.settings')
django.setup()

from scraper.models import Article, Post, Source
from scraper.tasks import scrape_social_media_source

def test_timezone_awareness():
    """Test that datetime objects are timezone aware"""
    print("Testing timezone awareness...")
    
    # Test creating an article with timezone-aware datetime
    source = Source.objects.first()
    if source:
        # Create a timezone-aware datetime
        published_at = timezone.now()
        print(f"Creating article with timezone-aware datetime: {published_at}")
        print(f"Timezone info: {published_at.tzinfo}")
        
        # Create article
        article = Article(
            title="Test Article",
            url="https://example.com/test",
            content="Test content",
            excerpt="Test excerpt",
            published_at=published_at,
            source=source
        )
        article.save()
        print(f"Article created successfully with scraped_at: {article.scraped_at}")
        print(f"Article scraped_at timezone info: {article.scraped_at.tzinfo}")
        
        # Clean up
        article.delete()
    
    print("Timezone awareness test completed!")

if __name__ == '__main__':
    test_timezone_awareness()