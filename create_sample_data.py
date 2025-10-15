import os
import django
from datetime import datetime, timedelta
from django.utils import timezone

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'osint_dashboard.settings')
django.setup()

from scraper.models import Article, Post, Source, Keyword
import random

def create_sample_articles():
    """
    Create sample articles for demonstration
    """
    # Get sources and keywords
    news_sources = Source.objects.filter(source_type='news')
    keywords = list(Keyword.objects.all())
    
    # Sample article data
    sample_articles = [
        {
            'title': 'Terrorism Threat in Major City',
            'url': 'https://example.com/article1',
            'content': 'Security officials are investigating a potential terrorism threat in the downtown area following reports of suspicious activity. Authorities have increased patrols and are urging citizens to remain vigilant.',
            'excerpt': 'Security officials are investigating a potential terrorism threat in the downtown area...',
            'published_at': timezone.now() - timedelta(days=1)
        },
        {
            'title': 'Cyber Attack on Government Systems',
            'url': 'https://example.com/article2',
            'content': 'A major cyber attack has compromised several government systems, raising concerns about national security. Experts are working to contain the breach and assess the damage.',
            'excerpt': 'A major cyber attack has compromised several government systems...',
            'published_at': timezone.now() - timedelta(days=2)
        },
        {
            'title': 'Protest Turns Violent',
            'url': 'https://example.com/article3',
            'content': 'What began as a peaceful demonstration has turned violent as protesters clashed with police. Several people were injured and numerous arrests were made.',
            'excerpt': 'What began as a peaceful demonstration has turned violent...',
            'published_at': timezone.now() - timedelta(days=3)
        },
        {
            'title': 'Security Measures Enhanced',
            'url': 'https://example.com/article4',
            'content': 'In response to recent security concerns, authorities have announced enhanced security measures at public venues and transportation hubs.',
            'excerpt': 'In response to recent security concerns, authorities have announced...',
            'published_at': timezone.now() - timedelta(hours=6)
        }
    ]
    
    source = news_sources.first()
    
    for article_data in sample_articles:
        # Check if article already exists
        article, created = Article.objects.get_or_create(
            url=article_data['url'],
            defaults={
                'title': article_data['title'],
                'content': article_data['content'],
                'excerpt': article_data['excerpt'],
                'published_at': article_data['published_at'],
                'source': source
            }
        )
        
        if created:
            # Add random keywords
            random_keywords = random.sample(keywords, random.randint(2, 5))
            article.keywords.set(random_keywords)
            print("Created article: {}".format(article.title))
        else:
            print("Article already exists: {}".format(article.title))

def create_sample_posts():
    """
    Create sample social media posts for demonstration
    """
    # Get sources and keywords
    social_sources = Source.objects.filter(source_type='social')
    keywords = list(Keyword.objects.all())
    
    # Sample post data
    sample_posts = [
        {
            'content': 'Just witnessed a suspicious package near the city hall. Reported to authorities. #security #safety',
            'url': 'https://twitter.com/user/status/1',
            'author': 'User1',
            'author_username': '@user1',
            'published_at': timezone.now() - timedelta(hours=2),
            'likes_count': 15,
            'retweets_count': 3,
            'replies_count': 2
        },
        {
            'content': 'Huge police presence downtown today. Wonder what\'s happening? #police #security',
            'url': 'https://twitter.com/user/status/2',
            'author': 'User2',
            'author_username': '@user2',
            'published_at': timezone.now() - timedelta(hours=5),
            'likes_count': 28,
            'retweets_count': 7,
            'replies_count': 5
        },
        {
            'content': 'Protesting the new security measures. Our freedom is being threatened! #protest #freedom',
            'url': 'https://twitter.com/user/status/3',
            'author': 'User3',
            'author_username': '@user3',
            'published_at': timezone.now() - timedelta(days=1),
            'likes_count': 112,
            'retweets_count': 45,
            'replies_count': 23
        },
        {
            'content': 'Another day, another terror alert. When will this end? #terrorism #fear',
            'url': 'https://twitter.com/user/status/4',
            'author': 'User4',
            'author_username': '@user4',
            'published_at': timezone.now() - timedelta(days=2),
            'likes_count': 76,
            'retweets_count': 32,
            'replies_count': 18
        }
    ]
    
    source = social_sources.first()
    
    for post_data in sample_posts:
        # Check if post already exists
        post, created = Post.objects.get_or_create(
            url=post_data['url'],
            defaults={
                'content': post_data['content'],
                'author': post_data['author'],
                'author_username': post_data['author_username'],
                'published_at': post_data['published_at'],
                'source': source,
                'likes_count': post_data['likes_count'],
                'retweets_count': post_data['retweets_count'],
                'replies_count': post_data['replies_count']
            }
        )
        
        if created:
            # Add random keywords
            random_keywords = random.sample(keywords, random.randint(1, 3))
            post.keywords.set(random_keywords)
            print("Created post: {}...".format(post.content[:50]))
        else:
            print("Post already exists: {}...".format(post.content[:50]))

if __name__ == '__main__':
    print("Creating sample articles...")
    create_sample_articles()
    
    print("\nCreating sample posts...")
    create_sample_posts()
    
    print("\nSample data creation completed!")