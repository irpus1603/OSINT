import os
import django
import json
from datetime import datetime, timedelta

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'osint_dashboard.settings')
django.setup()

from scraper.models import Article, Post, Source, Keyword
from analyzer.models import ArticleSentiment, PostSentiment

def test_enhanced_sentiment_data():
    """
    Test the enhanced sentiment data for the updated sentiment analysis page
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
    
    # Get sentiment data
    article_sentiments = ArticleSentiment.objects.filter(
        article__in=articles
    )
    
    post_sentiments = PostSentiment.objects.filter(
        post__in=posts
    )
    
    # Calculate total sentiment counts
    total_positive = article_sentiments.filter(sentiment='positive').count() + \
                    post_sentiments.filter(sentiment='positive').count()
    total_negative = article_sentiments.filter(sentiment='negative').count() + \
                    post_sentiments.filter(sentiment='negative').count()
    total_neutral = article_sentiments.filter(sentiment='neutral').count() + \
                   post_sentiments.filter(sentiment='neutral').count()
    
    print("=== ENHANCED SENTIMENT DATA ===")
    print(f"Total Positive: {total_positive}")
    print(f"Total Negative: {total_negative}")
    print(f"Total Neutral: {total_neutral}")
    
    # Calculate sentiment score
    total_sentiments = total_positive + total_negative + total_neutral
    if total_sentiments > 0:
        sentiment_score = round((total_positive - total_negative) / total_sentiments, 2)
        if sentiment_score > 0:
            sentiment_label = "Positive"
        elif sentiment_score < 0:
            sentiment_label = "Negative"
        else:
            sentiment_label = "Neutral"
    else:
        sentiment_score = 0
        sentiment_label = "Neutral"
    
    print(f"Sentiment Score: {sentiment_score} ({sentiment_label})")
    
    # Content type sentiment breakdown
    article_positive = article_sentiments.filter(sentiment='positive').count()
    article_negative = article_sentiments.filter(sentiment='negative').count()
    article_neutral = article_sentiments.filter(sentiment='neutral').count()
    
    post_positive = post_sentiments.filter(sentiment='positive').count()
    post_negative = post_sentiments.filter(sentiment='negative').count()
    post_neutral = post_sentiments.filter(sentiment='neutral').count()
    
    print("\n=== CONTENT TYPE BREAKDOWN ===")
    print(f"Articles - Positive: {article_positive}, Negative: {article_negative}, Neutral: {article_neutral}")
    print(f"Posts - Positive: {post_positive}, Negative: {post_negative}, Neutral: {post_neutral}")

if __name__ == '__main__':
    test_enhanced_sentiment_data()