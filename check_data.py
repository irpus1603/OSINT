import os
import django
from django.utils import timezone
from datetime import datetime, timedelta

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'osint_dashboard.settings')
django.setup()

from scraper.models import Source, Keyword, Article, Post
from analyzer.models import ArticleSentiment, PostSentiment, TrendingTopic

def check_data():
    print("Checking database content...")
    
    # Check sources
    sources = Source.objects.all()
    print(f"Sources: {sources.count()}")
    for source in sources:
        print(f"  - {source.name} ({source.source_type})")
    
    # Check keywords
    keywords = Keyword.objects.all()
    print(f"Keywords: {keywords.count()}")
    
    # Check articles
    articles = Article.objects.all()
    print(f"Articles: {articles.count()}")
    
    # Check posts
    posts = Post.objects.all()
    print(f"Posts: {posts.count()}")
    
    # Check sentiments
    article_sentiments = ArticleSentiment.objects.all()
    post_sentiments = PostSentiment.objects.all()
    print(f"Article Sentiments: {article_sentiments.count()}")
    print(f"Post Sentiments: {post_sentiments.count()}")
    
    # Check trending topics
    trending_topics = TrendingTopic.objects.all()
    print(f"Trending Topics: {trending_topics.count()}")
    
    # Print some sample data
    if articles.exists():
        print("\nSample Articles:")
        for article in articles[:3]:
            print(f"  - {article.title[:50]}...")
    
    if posts.exists():
        print("\nSample Posts:")
        for post in posts[:3]:
            print(f"  - {post.content[:50]}...")

if __name__ == '__main__':
    check_data()