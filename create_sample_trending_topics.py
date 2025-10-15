import os
import django
import json
from datetime import datetime, timedelta

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'osint_dashboard.settings')
django.setup()

from analyzer.models import TrendingTopic

def create_sample_trending_topics():
    """
    Create sample trending topics for demonstration
    """
    # Sample trending topics data
    sample_topics = [
        {
            'keyword': 'terrorism',
            'frequency': 25,
            'sentiment_distribution': {
                'positive': 2,
                'negative': 18,
                'neutral': 5
            },
            'date': datetime.now().date()
        },
        {
            'keyword': 'cyber attack',
            'frequency': 18,
            'sentiment_distribution': {
                'positive': 1,
                'negative': 15,
                'neutral': 2
            },
            'date': datetime.now().date()
        },
        {
            'keyword': 'protest',
            'frequency': 15,
            'sentiment_distribution': {
                'positive': 3,
                'negative': 8,
                'neutral': 4
            },
            'date': datetime.now().date()
        },
        {
            'keyword': 'security',
            'frequency': 12,
            'sentiment_distribution': {
                'positive': 4,
                'negative': 5,
                'neutral': 3
            },
            'date': datetime.now().date()
        },
        {
            'keyword': 'threat',
            'frequency': 10,
            'sentiment_distribution': {
                'positive': 1,
                'negative': 7,
                'neutral': 2
            },
            'date': datetime.now().date()
        }
    ]
    
    for topic_data in sample_topics:
        # Check if topic already exists
        topic, created = TrendingTopic.objects.get_or_create(
            keyword=topic_data['keyword'],
            date=topic_data['date'],
            defaults={
                'frequency': topic_data['frequency'],
                'sentiment_distribution': topic_data['sentiment_distribution']
            }
        )
        
        if created:
            print(f"Created trending topic: {topic.keyword}")
        else:
            print(f"Trending topic already exists: {topic.keyword}")

if __name__ == '__main__':
    print("Creating sample trending topics...")
    create_sample_trending_topics()
    print("Sample trending topics creation completed!")