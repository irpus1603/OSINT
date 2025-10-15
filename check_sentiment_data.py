import os
import django

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'osint_dashboard.settings')
django.setup()

from scraper.models import Article, Post
from analyzer.models import ArticleSentiment, PostSentiment

def check_sentiment_data():
    """
    Check existing sentiment data
    """
    articles = Article.objects.all()
    posts = Post.objects.all()
    
    print(f"Total articles: {articles.count()}")
    print(f"Total posts: {posts.count()}")
    
    article_sentiments = ArticleSentiment.objects.all()
    post_sentiments = PostSentiment.objects.all()
    
    print(f"Articles with sentiment: {article_sentiments.count()}")
    print(f"Posts with sentiment: {post_sentiments.count()}")
    
    print("\nArticle sentiments:")
    for sentiment in article_sentiments:
        print(f"  {sentiment.article.title[:50]}... - {sentiment.sentiment} ({sentiment.confidence_score:.2f})")
    
    print("\nPost sentiments:")
    for sentiment in post_sentiments:
        print(f"  {sentiment.post.content[:50]}... - {sentiment.sentiment} ({sentiment.confidence_score:.2f})")

if __name__ == '__main__':
    check_sentiment_data()