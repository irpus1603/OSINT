import os
import django

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'osint_dashboard.settings')
django.setup()

from textblob import TextBlob
from analyzer.models import ArticleSentiment, PostSentiment
from scraper.models import Article, Post
import logging
from datetime import datetime

# Import VADER for better social media sentiment analysis
try:
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
    VADER_AVAILABLE = True
except ImportError:
    print("VADER not available. Install with: pip install vaderSentiment")
    VADER_AVAILABLE = False

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize VADER analyzer if available
if VADER_AVAILABLE:
    vader_analyzer = SentimentIntensityAnalyzer()

def analyze_sentiment(text, content_type='article'):
    """
    Enhanced sentiment analysis using multiple approaches
    - Uses VADER for social media content (posts)
    - Uses TextBlob for news articles
    - Combines both for better accuracy
    
    Args:
        text (str): Text to analyze
        content_type (str): 'article' or 'post' to optimize analysis method
        
    Returns:
        tuple: (sentiment_label, confidence_score, analysis_method)
    """
    if not text or not text.strip():
        return 'neutral', 0.0, 'empty_text'
    
    text = text.strip()
    logger.debug(f"Analyzing sentiment for {content_type}: {text[:100]}...")
    
    # Method 1: VADER Analysis (better for social media, informal text)
    vader_sentiment = None
    vader_confidence = 0.0
    
    if VADER_AVAILABLE:
        scores = vader_analyzer.polarity_scores(text)
        compound = scores['compound']
        
        if compound >= 0.05:
            vader_sentiment = 'positive'
        elif compound <= -0.05:
            vader_sentiment = 'negative'
        else:
            vader_sentiment = 'neutral'
        
        vader_confidence = abs(compound)
        logger.debug(f"VADER scores: {scores} -> {vader_sentiment} ({vader_confidence:.3f})")
    
    # Method 2: TextBlob Analysis (better for formal text, articles)
    try:
        blob = TextBlob(text)
        polarity = blob.sentiment.polarity
        
        if polarity > 0.1:
            textblob_sentiment = 'positive'
        elif polarity < -0.1:
            textblob_sentiment = 'negative'
        else:
            textblob_sentiment = 'neutral'
        
        textblob_confidence = abs(polarity)
        logger.debug(f"TextBlob polarity: {polarity:.3f} -> {textblob_sentiment} ({textblob_confidence:.3f})")
    except Exception as e:
        logger.warning(f"TextBlob analysis failed: {e}")
        textblob_sentiment = 'neutral'
        textblob_confidence = 0.0
    
    # Combine methods based on content type and confidence
    if content_type == 'post' and VADER_AVAILABLE:
        # Prefer VADER for social media posts
        if vader_confidence > 0.3:  # High confidence VADER result
            return vader_sentiment, vader_confidence, 'vader'
        elif textblob_confidence > 0.2:  # Fallback to TextBlob
            return textblob_sentiment, textblob_confidence, 'textblob_fallback'
        else:
            return vader_sentiment, vader_confidence, 'vader_low_confidence'
    
    elif content_type == 'article':
        # Prefer TextBlob for news articles, but use VADER as validation
        if textblob_confidence > 0.2:
            # If both methods agree, increase confidence
            if VADER_AVAILABLE and vader_sentiment == textblob_sentiment and vader_confidence > 0.2:
                combined_confidence = min(0.95, (textblob_confidence + vader_confidence) / 2 + 0.1)
                return textblob_sentiment, combined_confidence, 'combined_agreement'
            else:
                return textblob_sentiment, textblob_confidence, 'textblob'
        elif VADER_AVAILABLE and vader_confidence > 0.3:
            return vader_sentiment, vader_confidence, 'vader_fallback'
        else:
            return textblob_sentiment, max(textblob_confidence, vader_confidence), 'low_confidence'
    
    # Default fallback
    if VADER_AVAILABLE:
        return vader_sentiment, vader_confidence, 'vader_default'
    else:
        return textblob_sentiment, textblob_confidence, 'textblob_default'

def detect_security_sentiment_indicators(text):
    """
    Detect security/threat-related sentiment indicators
    Returns adjustment factor for sentiment confidence
    """
    if not text:
        return 1.0
    
    text_lower = text.lower()
    
    # Security threat keywords that typically indicate negative sentiment
    threat_keywords = [
        'terror', 'attack', 'bomb', 'explosion', 'threat', 'violence',
        'kill', 'death', 'murder', 'shoot', 'gun', 'weapon', 'militant',
        'extremist', 'radical', 'danger', 'emergency', 'crisis', 'risk',
        # Indonesian keywords
        'teror', 'serangan', 'bom', 'ledakan', 'ancaman', 'kekerasan',
        'bunuh', 'tembak', 'senjata', 'militan', 'ekstremis', 'radikal'
    ]
    
    # Security positive keywords
    security_positive = [
        'secure', 'safe', 'protected', 'defense', 'peace', 'stability',
        'prevention', 'captured', 'arrested', 'neutralized', 'success',
        # Indonesian
        'aman', 'selamat', 'damai', 'stabilitas', 'pencegahan', 'tertangkap'
    ]
    
    threat_count = sum(1 for keyword in threat_keywords if keyword in text_lower)
    positive_count = sum(1 for keyword in security_positive if keyword in text_lower)
    
    if threat_count > 0:
        # Boost confidence for threat-related negative sentiment
        return min(1.5, 1.0 + (threat_count * 0.1))
    elif positive_count > 0:
        # Boost confidence for security-positive sentiment
        return min(1.3, 1.0 + (positive_count * 0.05))
    
    return 1.0

def analyze_article_sentiments():
    """
    Analyze sentiments for all articles that don't have sentiment analysis yet
    """
    articles = Article.objects.filter(sentiment__isnull=True)
    logger.info(f"Analyzing sentiment for {articles.count()} articles...")
    
    analyzed_count = 0
    error_count = 0
    
    for article in articles:
        try:
            # Use enhanced sentiment analysis for articles
            text = f"{article.title}\n{article.content}" if article.title else article.content
            sentiment, confidence, method = analyze_sentiment(text, content_type='article')
            
            # Apply security-specific sentiment adjustments
            security_factor = detect_security_sentiment_indicators(text)
            adjusted_confidence = min(1.0, confidence * security_factor)
            
            ArticleSentiment.objects.create(
                article=article,
                text=article.content,
                sentiment=sentiment,
                confidence_score=adjusted_confidence
            )
            
            analyzed_count += 1
            logger.info(f"✅ Article {analyzed_count}: {article.title[:50]}... -> {sentiment} ({adjusted_confidence:.3f}, {method})")
            
            if security_factor > 1.0:
                logger.info(f"   🔒 Security context detected (boost: {security_factor:.2f}x)")
                
        except Exception as e:
            error_count += 1
            logger.error(f"❌ Error analyzing article '{article.title[:30]}': {e}")
    
    logger.info(f"Article sentiment analysis completed: {analyzed_count} analyzed, {error_count} errors")

def analyze_post_sentiments():
    """
    Analyze sentiments for all posts that don't have sentiment analysis yet
    """
    posts = Post.objects.filter(sentiment__isnull=True)
    logger.info(f"Analyzing sentiment for {posts.count()} posts...")
    
    analyzed_count = 0
    error_count = 0
    
    for post in posts:
        try:
            # Use enhanced sentiment analysis optimized for social media posts
            sentiment, confidence, method = analyze_sentiment(post.content, content_type='post')
            
            # Apply security-specific sentiment adjustments
            security_factor = detect_security_sentiment_indicators(post.content)
            adjusted_confidence = min(1.0, confidence * security_factor)
            
            PostSentiment.objects.create(
                post=post,
                text=post.content,
                sentiment=sentiment,
                confidence_score=adjusted_confidence
            )
            
            analyzed_count += 1
            logger.info(f"✅ Post {analyzed_count}: {post.content[:50]}... -> {sentiment} ({adjusted_confidence:.3f}, {method})")
            
            if security_factor > 1.0:
                logger.info(f"   🔒 Security context detected (boost: {security_factor:.2f}x)")
                
        except Exception as e:
            error_count += 1
            logger.error(f"❌ Error analyzing post '{post.content[:30]}': {e}")
    
    logger.info(f"Post sentiment analysis completed: {analyzed_count} analyzed, {error_count} errors")

def reanalyze_all_sentiments(force=False):
    """
    Reanalyze all sentiments with the new enhanced algorithm
    
    Args:
        force (bool): If True, reanalyze even items that already have sentiment data
    """
    logger.info("🔄 Starting comprehensive sentiment reanalysis...")
    
    if force:
        # Delete existing sentiment data to force reanalysis
        ArticleSentiment.objects.all().delete()
        PostSentiment.objects.all().delete()
        logger.info("🗑️ Deleted existing sentiment data for fresh analysis")
    
    # Analyze articles and posts
    analyze_article_sentiments()
    analyze_post_sentiments()
    
    # Generate summary statistics
    generate_sentiment_summary()
    
    logger.info("✅ Comprehensive sentiment analysis completed!")

def generate_sentiment_summary():
    """
    Generate and display sentiment analysis summary statistics
    """
    article_sentiments = ArticleSentiment.objects.all()
    post_sentiments = PostSentiment.objects.all()
    
    # Article statistics
    article_stats = {
        'total': article_sentiments.count(),
        'positive': article_sentiments.filter(sentiment='positive').count(),
        'negative': article_sentiments.filter(sentiment='negative').count(),
        'neutral': article_sentiments.filter(sentiment='neutral').count(),
    }
    
    # Post statistics
    post_stats = {
        'total': post_sentiments.count(),
        'positive': post_sentiments.filter(sentiment='positive').count(),
        'negative': post_sentiments.filter(sentiment='negative').count(),
        'neutral': post_sentiments.filter(sentiment='neutral').count(),
    }
    
    logger.info("📊 SENTIMENT ANALYSIS SUMMARY:")
    logger.info(f"📰 Articles: {article_stats['total']} total")
    logger.info(f"   ✅ Positive: {article_stats['positive']} ({article_stats['positive']/max(1,article_stats['total'])*100:.1f}%)")
    logger.info(f"   ❌ Negative: {article_stats['negative']} ({article_stats['negative']/max(1,article_stats['total'])*100:.1f}%)")
    logger.info(f"   ⚪ Neutral: {article_stats['neutral']} ({article_stats['neutral']/max(1,article_stats['total'])*100:.1f}%)")
    
    logger.info(f"💬 Posts: {post_stats['total']} total")
    logger.info(f"   ✅ Positive: {post_stats['positive']} ({post_stats['positive']/max(1,post_stats['total'])*100:.1f}%)")
    logger.info(f"   ❌ Negative: {post_stats['negative']} ({post_stats['negative']/max(1,post_stats['total'])*100:.1f}%)")
    logger.info(f"   ⚪ Neutral: {post_stats['neutral']} ({post_stats['neutral']/max(1,post_stats['total'])*100:.1f}%)")
    
    # High confidence analysis
    high_conf_articles = article_sentiments.filter(confidence_score__gte=0.5).count()
    high_conf_posts = post_sentiments.filter(confidence_score__gte=0.5).count()
    
    logger.info(f"🎯 High Confidence (≥0.5): Articles {high_conf_articles}/{article_stats['total']}, Posts {high_conf_posts}/{post_stats['total']}")

def test_sentiment_analysis():
    """
    Test the sentiment analysis with sample texts
    """
    test_cases = [
        ("This is a great day! Everything is wonderful.", "positive"),
        ("Terrible attack happened today. Many people were killed.", "negative"),
        ("The weather is okay today.", "neutral"),
        ("BREAKING: Terror attack in central Jakarta kills 5 people", "negative"),
        ("Police successfully captured the terrorist before any harm", "positive"),
        ("Serangan teroris di Jakarta hari ini sangat mengerikan", "negative"),  # Indonesian
        ("Keamanan nasional berhasil dicapai dengan baik", "positive"),  # Indonesian
    ]
    
    logger.info("🧪 Testing sentiment analysis with sample cases...")
    
    for i, (text, expected) in enumerate(test_cases, 1):
        sentiment, confidence, method = analyze_sentiment(text)
        security_factor = detect_security_sentiment_indicators(text)
        
        status = "✅" if sentiment == expected else "❌"
        logger.info(f"{status} Test {i}: '{text[:60]}...' -> {sentiment} ({confidence:.3f}, {method}, security:{security_factor:.2f}x)")
        logger.info(f"     Expected: {expected}, Got: {sentiment}")
    
    logger.info("🧪 Sentiment analysis testing completed!")

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == 'test':
            # Test the sentiment analysis
            test_sentiment_analysis()
        elif command == 'reanalyze' or command == 'force':
            # Force reanalysis of all content
            reanalyze_all_sentiments(force=True)
        elif command == 'summary':
            # Generate summary only
            generate_sentiment_summary()
        elif command == 'install-vader':
            # Install VADER
            import subprocess
            try:
                subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'vaderSentiment'])
                logger.info("✅ VADER sentiment analyzer installed successfully!")
            except Exception as e:
                logger.error(f"❌ Failed to install VADER: {e}")
        else:
            logger.error(f"Unknown command: {command}")
            logger.info("Available commands: test, reanalyze, summary, install-vader")
    else:
        # Default: analyze new content only
        logger.info("🚀 Starting enhanced sentiment analysis...")
        logger.info("💡 Use 'python analyze_sentiment.py test' to test the system")
        logger.info("💡 Use 'python analyze_sentiment.py reanalyze' to reanalyze all content with new algorithm")
        logger.info("💡 Use 'python analyze_sentiment.py install-vader' to install VADER for better social media analysis")
        
        analyze_article_sentiments()
        analyze_post_sentiments()
        generate_sentiment_summary()
        
        logger.info("✅ Enhanced sentiment analysis completed!")