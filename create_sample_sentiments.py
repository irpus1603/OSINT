import os
import django
import random

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'osint_dashboard.settings')
django.setup()

from textblob import TextBlob
from analyzer.models import ArticleSentiment, PostSentiment
from scraper.models import Article, Post

def create_sample_sentiments():
    """
    Create sample sentiment data for demonstration
    """
    # Get all articles and posts
    articles = Article.objects.all()
    posts = Post.objects.all()
    
    print(f"Creating sentiment data for {articles.count()} articles and {posts.count()} posts...")
    
    # Create sample sentiments for articles
    for article in articles:
        # Check if sentiment already exists
        if not hasattr(article, 'sentiment'):
            # Generate random sentiment for demo
            sentiments = ['positive', 'negative', 'neutral']
            sentiment = random.choice(sentiments)
            
            # Generate confidence score
            confidence = random.uniform(0.5, 1.0)
            
            ArticleSentiment.objects.create(
                article=article,
                text=article.content,
                sentiment=sentiment,
                confidence_score=confidence
            )
            print(f"Created sentiment for article: {article.title[:50]}... - {sentiment}")
    
    # Create sample sentiments for posts
    for post in posts:
        # Check if sentiment already exists
        if not hasattr(post, 'sentiment'):
            # Generate random sentiment for demo
            sentiments = ['positive', 'negative', 'neutral']
            sentiment = random.choice(sentiments)
            
            # Generate confidence score
            confidence = random.uniform(0.5, 1.0)
            
            PostSentiment.objects.create(
                post=post,
                text=post.content,
                sentiment=sentiment,
                confidence_score=confidence
            )
            print(f"Created sentiment for post: {post.content[:50]}... - {sentiment}")

if __name__ == '__main__':
    print("Creating sample sentiment data...")
    create_sample_sentiments()
    print("Sample sentiment data creation completed!")