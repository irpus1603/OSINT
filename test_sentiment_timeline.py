import os
import django
import json
from datetime import datetime, timedelta

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'osint_dashboard.settings')
django.setup()

from scraper.models import Article, Post, Source, Keyword
from analyzer.models import ArticleSentiment, PostSentiment

def test_sentiment_timeline_data():
    """
    Test the sentiment timeline data to see what's being generated
    """
    # Get all sources and keywords
    sources = Source.objects.all()
    
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
    
    # Get sentiment data over time
    sentiment_timeline = []
    current_date = start_date
    while current_date <= end_date:
        next_date = current_date + timedelta(days=1)
        
        article_sentiments = ArticleSentiment.objects.filter(
            article__in=articles.filter(scraped_at__range=(current_date, next_date))
        )
        
        post_sentiments = PostSentiment.objects.filter(
            post__in=posts.filter(scraped_at__range=(current_date, next_date))
        )
        
        sentiment_data = {
            'date': current_date.strftime('%Y-%m-%d'),
            'positive': article_sentiments.filter(sentiment='positive').count() + 
                       post_sentiments.filter(sentiment='positive').count(),
            'negative': article_sentiments.filter(sentiment='negative').count() + 
                       post_sentiments.filter(sentiment='negative').count(),
            'neutral': article_sentiments.filter(sentiment='neutral').count() + 
                      post_sentiments.filter(sentiment='neutral').count(),
        }
        
        sentiment_timeline.append(sentiment_data)
        current_date = next_date
    
    print("=== SENTIMENT TIMELINE DATA ===")
    print(json.dumps(sentiment_timeline, indent=2))

if __name__ == '__main__':
    test_sentiment_timeline_data()