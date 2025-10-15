import os
import django
import json
from datetime import datetime, timedelta

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'osint_dashboard.settings')
django.setup()

from scraper.models import Article, Post, Source, Keyword
from analyzer.models import ArticleSentiment, PostSentiment, TrendingTopic

def test_dashboard_data():
    """
    Test the dashboard data to see what's being generated
    """
    # Get all sources and keywords
    sources = Source.objects.all()
    keywords = Keyword.objects.all()
    
    # Set date range
    date_range = '7d'
    end_date = datetime.now()
    if date_range == '1d':
        start_date = end_date - timedelta(days=1)
    elif date_range == '7d':
        start_date = end_date - timedelta(days=7)
    elif date_range == '30d':
        start_date = end_date - timedelta(days=30)
    else:  # 90d
        start_date = end_date - timedelta(days=90)
    
    # Filter data by date range
    articles = Article.objects.filter(
        scraped_at__range=(start_date, end_date),
        source__in=sources
    )
    
    posts = Post.objects.filter(
        scraped_at__range=(start_date, end_date),
        source__in=sources
    )
    
    # Get sentiment data
    article_sentiments = ArticleSentiment.objects.filter(
        article__in=articles
    )
    
    post_sentiments = PostSentiment.objects.filter(
        post__in=posts
    )
    
    # Calculate sentiment distribution
    sentiment_data = {
        'positive': article_sentiments.filter(sentiment='positive').count() + 
                   post_sentiments.filter(sentiment='positive').count(),
        'negative': article_sentiments.filter(sentiment='negative').count() + 
                   post_sentiments.filter(sentiment='negative').count(),
        'neutral': article_sentiments.filter(sentiment='neutral').count() + 
                  post_sentiments.filter(sentiment='neutral').count(),
    }
    
    # Get trending topics
    trending_topics = TrendingTopic.objects.filter(
        date__range=(start_date.date(), end_date.date())
    ).order_by('-frequency')[:10]
    
    # Get source distribution
    source_distribution = {}
    for source in sources:
        article_count = articles.filter(source=source).count()
        post_count = posts.filter(source=source).count()
        source_distribution[source.name] = article_count + post_count
    
    # Print all data for debugging
    print("=== DASHBOARD DATA ===")
    print(f"Date range: {date_range}")
    print(f"Total articles: {articles.count()}")
    print(f"Total posts: {posts.count()}")
    print(f"Article sentiments: {article_sentiments.count()}")
    print(f"Post sentiments: {post_sentiments.count()}")
    print(f"Trending topics: {trending_topics.count()}")
    
    print("\n=== SENTIMENT DATA ===")
    print(json.dumps(sentiment_data, indent=2))
    
    print("\n=== SOURCE DISTRIBUTION ===")
    print(json.dumps(source_distribution, indent=2))
    
    print("\n=== TRENDING TOPICS ===")
    for topic in trending_topics:
        print(f"{topic.keyword}: {topic.frequency}")
        print(f"  Sentiment distribution: {topic.sentiment_distribution}")

if __name__ == '__main__':
    test_dashboard_data()