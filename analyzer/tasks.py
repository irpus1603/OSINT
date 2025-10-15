from celery import shared_task
from django.utils import timezone
import logging

# Set up logging
logger = logging.getLogger(__name__)

@shared_task
def run_sentiment_analysis():
    """
    Celery task to run sentiment analysis on new articles and posts
    """
    try:
        # Import here to avoid circular imports
        import os
        import sys
        sys.path.append(os.path.dirname(os.path.dirname(__file__)))
        
        from analyze_sentiment import analyze_article_sentiments, analyze_post_sentiments, generate_sentiment_summary
        
        logger.info("🚀 Starting automated sentiment analysis...")
        
        # Analyze new content
        analyze_article_sentiments()
        analyze_post_sentiments()
        
        # Generate summary
        generate_sentiment_summary()
        
        logger.info("✅ Automated sentiment analysis completed!")
        return "Sentiment analysis completed successfully"
        
    except Exception as e:
        error_msg = f"Error in automated sentiment analysis: {str(e)}"
        logger.error(error_msg)
        return error_msg

@shared_task  
def analyze_single_article(article_id):
    """
    Analyze sentiment for a single article
    """
    try:
        from analyzer.models import ArticleSentiment
        from scraper.models import Article
        from analyze_sentiment import analyze_sentiment, detect_security_sentiment_indicators
        
        article = Article.objects.get(id=article_id)
        
        # Skip if already analyzed
        if ArticleSentiment.objects.filter(article=article).exists():
            return f"Article {article_id} already has sentiment analysis"
        
        # Analyze sentiment
        text = f"{article.title}\n{article.content}" if article.title else article.content
        sentiment, confidence, method = analyze_sentiment(text, content_type='article')
        
        # Apply security-specific adjustments
        security_factor = detect_security_sentiment_indicators(text)
        adjusted_confidence = min(1.0, confidence * security_factor)
        
        # Save result
        ArticleSentiment.objects.create(
            article=article,
            text=article.content,
            sentiment=sentiment,
            confidence_score=adjusted_confidence
        )
        
        logger.info(f"✅ Analyzed article {article_id}: {sentiment} ({adjusted_confidence:.3f})")
        return f"Article {article_id} analyzed: {sentiment}"
        
    except Exception as e:
        error_msg = f"Error analyzing article {article_id}: {str(e)}"
        logger.error(error_msg)
        return error_msg

@shared_task
def analyze_single_post(post_id):
    """
    Analyze sentiment for a single social media post
    """
    try:
        from analyzer.models import PostSentiment
        from scraper.models import Post
        from analyze_sentiment import analyze_sentiment, detect_security_sentiment_indicators
        
        post = Post.objects.get(id=post_id)
        
        # Skip if already analyzed
        if PostSentiment.objects.filter(post=post).exists():
            return f"Post {post_id} already has sentiment analysis"
        
        # Analyze sentiment
        sentiment, confidence, method = analyze_sentiment(post.content, content_type='post')
        
        # Apply security-specific adjustments
        security_factor = detect_security_sentiment_indicators(post.content)
        adjusted_confidence = min(1.0, confidence * security_factor)
        
        # Save result
        PostSentiment.objects.create(
            post=post,
            text=post.content,
            sentiment=sentiment,
            confidence_score=adjusted_confidence
        )
        
        logger.info(f"✅ Analyzed post {post_id}: {sentiment} ({adjusted_confidence:.3f})")
        return f"Post {post_id} analyzed: {sentiment}"
        
    except Exception as e:
        error_msg = f"Error analyzing post {post_id}: {str(e)}"
        logger.error(error_msg)
        return error_msg