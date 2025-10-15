import os
import django

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'osint_dashboard.settings')
django.setup()

from django.contrib.auth import get_user_model
from scraper.models import Source, Keyword, Article, Post
from analyzer.models import ArticleSentiment, PostSentiment
from scheduler.models import CrawlTask, CrawlLog

def test_django_setup():
    """Test that all Django components are working"""
    print("Testing Django setup...")
    
    # Test database access
    User = get_user_model()
    user_count = User.objects.count()
    print(f"Users in database: {user_count}")
    
    # Test scraper models
    source_count = Source.objects.count()
    keyword_count = Keyword.objects.count()
    article_count = Article.objects.count()
    post_count = Post.objects.count()
    print(f"Sources: {source_count}")
    print(f"Keywords: {keyword_count}")
    print(f"Articles: {article_count}")
    print(f"Posts: {post_count}")
    
    # Test analyzer models
    article_sentiment_count = ArticleSentiment.objects.count()
    post_sentiment_count = PostSentiment.objects.count()
    print(f"Article Sentiments: {article_sentiment_count}")
    print(f"Post Sentiments: {post_sentiment_count}")
    
    # Test scheduler models
    crawl_task_count = CrawlTask.objects.count()
    crawl_log_count = CrawlLog.objects.count()
    print(f"Crawl Tasks: {crawl_task_count}")
    print(f"Crawl Logs: {crawl_log_count}")
    
    print("Django setup test completed successfully!")

if __name__ == '__main__':
    test_django_setup()