import os
import django
from django.utils import timezone
from datetime import datetime, timedelta
import random

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'osint_dashboard.settings')
django.setup()

from scraper.models import Keyword
from analyzer.models import TrendingTopic

def create_trending_topics():
    print("Creating sample trending topics...")
    
    # Get some keywords
    keywords = list(Keyword.objects.all()[:10])
    
    # Create sample trending topics
    today = timezone.now().date()
    
    for i in range(5):
        keyword = random.choice(keywords)
        frequency = random.randint(10, 100)
        sentiment_distribution = {
            'positive': random.randint(0, frequency),
            'negative': random.randint(0, frequency),
            'neutral': frequency - (random.randint(0, frequency) + random.randint(0, frequency))
        }
        
        # Ensure neutral is non-negative
        sentiment_distribution['neutral'] = max(0, sentiment_distribution['neutral'])
        
        trending_topic, created = TrendingTopic.objects.get_or_create(
            keyword=keyword.term,
            date=today - timedelta(days=i),
            defaults={
                'frequency': frequency,
                'sentiment_distribution': sentiment_distribution
            }
        )
        
        if created:
            print(f"Created trending topic: {trending_topic.keyword} (Frequency: {trending_topic.frequency})")
        else:
            print(f"Trending topic already exists: {trending_topic.keyword}")

if __name__ == '__main__':
    create_trending_topics()