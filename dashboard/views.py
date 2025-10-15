import json
import logging
from django.shortcuts import render
# from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from django.db.models import Count, Q
from django.template.loader import render_to_string
from scraper.models import Article, Post, Keyword, Source
from analyzer.models import ArticleSentiment, PostSentiment, TrendingTopic
from scheduler.models import CrawlTask
from dashboard.models import DashboardConfig, Alert
from datetime import datetime, timedelta
import weasyprint
from weasyprint import HTML, CSS
from io import BytesIO

logger = logging.getLogger(__name__)

# @login_required
def dashboard_view(request):
    # Get user's dashboard configuration
    # For development, we'll use default configuration
    keywords = Keyword.objects.all()
    sources = Source.objects.all()
    date_range = '7d'
    
    # Calculate date range
    end_date = datetime.now()
    if date_range == '1d':
        start_date = end_date - timedelta(days=1)
    elif date_range == '7d':
        start_date = end_date - timedelta(days=7)
    elif date_range == '30d':
        start_date = end_date - timedelta(days=30)
    else:  # 90d
        start_date = end_date - timedelta(days=90)
    
    # Filter data by date range and user preferences
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
    
    context = {
        'sentiment_data': sentiment_data,
        'trending_topics': trending_topics,
        'source_distribution': json.dumps(source_distribution),
        'total_articles': articles.count(),
        'total_posts': posts.count(),
        'date_range': date_range,
    }
    
    return render(request, 'dashboard/index.html', context)

# @login_required
def sentiment_analysis_view(request):
    # For development, we'll use default configuration
    keywords = Keyword.objects.all()
    sources = Source.objects.all()
    date_range = '7d'
    
    # Calculate date range
    end_date = datetime.now()
    if date_range == '1d':
        start_date = end_date - timedelta(days=1)
    elif date_range == '7d':
        start_date = end_date - timedelta(days=7)
    elif date_range == '30d':
        start_date = end_date - timedelta(days=30)
    else:  # 90d
        start_date = end_date - timedelta(days=90)
    
    # Filter data by date range and user preferences
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
    
    # Calculate sentiment score (-1 to 1 scale)
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
    
    # Get sentiment data over time
    sentiment_timeline = []
    peak_sentiment_count = 0
    peak_sentiment_day = ""
    
    current_date = start_date
    while current_date <= end_date:
        next_date = current_date + timedelta(days=1)
        
        article_sentiments_time = ArticleSentiment.objects.filter(
            article__in=articles.filter(scraped_at__range=(current_date, next_date))
        )
        
        post_sentiments_time = PostSentiment.objects.filter(
            post__in=posts.filter(scraped_at__range=(current_date, next_date))
        )
        
        day_positive = article_sentiments_time.filter(sentiment='positive').count() + \
                      post_sentiments_time.filter(sentiment='positive').count()
        day_negative = article_sentiments_time.filter(sentiment='negative').count() + \
                      post_sentiments_time.filter(sentiment='negative').count()
        day_neutral = article_sentiments_time.filter(sentiment='neutral').count() + \
                     post_sentiments_time.filter(sentiment='neutral').count()
        
        day_total = day_positive + day_negative + day_neutral
        
        # Track peak sentiment day
        if day_total > peak_sentiment_count:
            peak_sentiment_count = day_total
            peak_sentiment_day = current_date.strftime('%Y-%m-%d')
        
        sentiment_data = {
            'date': current_date.strftime('%Y-%m-%d'),
            'positive': day_positive,
            'negative': day_negative,
            'neutral': day_neutral,
        }
        
        sentiment_timeline.append(sentiment_data)
        current_date = next_date
    
    # Determine trend direction (simplified)
    if len(sentiment_timeline) >= 2:
        first_week_total = sum([
            sentiment_timeline[i]['positive'] + 
            sentiment_timeline[i]['negative'] + 
            sentiment_timeline[i]['neutral'] 
            for i in range(min(3, len(sentiment_timeline)))
        ])
        last_week_total = sum([
            sentiment_timeline[i]['positive'] + 
            sentiment_timeline[i]['negative'] + 
            sentiment_timeline[i]['neutral'] 
            for i in range(max(0, len(sentiment_timeline) - 3), len(sentiment_timeline))
        ])
        
        if last_week_total > first_week_total:
            trend_direction = "increasing"
        elif last_week_total < first_week_total:
            trend_direction = "decreasing"
        else:
            trend_direction = "stable"
    else:
        trend_direction = "insufficient data"
    
    # Content type sentiment breakdown
    article_positive = article_sentiments.filter(sentiment='positive').count()
    article_negative = article_sentiments.filter(sentiment='negative').count()
    article_neutral = article_sentiments.filter(sentiment='neutral').count()
    
    post_positive = post_sentiments.filter(sentiment='positive').count()
    post_negative = post_sentiments.filter(sentiment='negative').count()
    post_neutral = post_sentiments.filter(sentiment='neutral').count()
    
    # Set recommendation based on sentiment
    if total_negative > total_positive:
        recommendation = "negative sentiment trends"
    elif total_positive > total_negative:
        recommendation = "positive sentiment trends"
    else:
        recommendation = "overall sentiment patterns"
    
    context = {
        'sentiment_timeline': json.dumps(sentiment_timeline),
        'date_range': date_range,
        'total_positive': total_positive,
        'total_negative': total_negative,
        'total_neutral': total_neutral,
        'sentiment_score': f"{sentiment_score} ({sentiment_label})",
        'trend_direction': trend_direction,
        'peak_sentiment_day': peak_sentiment_day,
        'peak_sentiment_count': peak_sentiment_count,
        'recommendation': recommendation,
        'article_positive': article_positive,
        'article_negative': article_negative,
        'article_neutral': article_neutral,
        'post_positive': post_positive,
        'post_negative': post_negative,
        'post_neutral': post_neutral,
    }
    
    return render(request, 'dashboard/sentiment_analysis.html', context)

# @login_required
def sources_view(request):
    # For development, we'll use default configuration
    keywords = Keyword.objects.all()
    sources = Source.objects.all()
    date_range = '7d'
    
    # Calculate date range
    end_date = datetime.now()
    if date_range == '1d':
        start_date = end_date - timedelta(days=1)
    elif date_range == '7d':
        start_date = end_date - timedelta(days=7)
    elif date_range == '30d':
        start_date = end_date - timedelta(days=30)
    else:  # 90d
        start_date = end_date - timedelta(days=90)
    
    # Get source data
    source_data = []
    for source in sources:
        articles = Article.objects.filter(
            source=source,
            scraped_at__range=(start_date, end_date)
        )
        
        posts = Post.objects.filter(
            source=source,
            scraped_at__range=(start_date, end_date)
        )
        
        article_sentiments = ArticleSentiment.objects.filter(
            article__in=articles
        )
        
        post_sentiments = PostSentiment.objects.filter(
            post__in=posts
        )
        
        source_info = {
            'name': source.name,
            'type': source.source_type,
            'total_items': articles.count() + posts.count(),
            'positive_sentiment': article_sentiments.filter(sentiment='positive').count() + 
                                 post_sentiments.filter(sentiment='positive').count(),
            'negative_sentiment': article_sentiments.filter(sentiment='negative').count() + 
                                 post_sentiments.filter(sentiment='negative').count(),
            'neutral_sentiment': article_sentiments.filter(sentiment='neutral').count() + 
                                post_sentiments.filter(sentiment='neutral').count(),
        }
        
        source_data.append(source_info)
    
    context = {
        'source_data': source_data,
        'date_range': date_range,
    }
    
    return render(request, 'dashboard/sources.html', context)

# @login_required
def alerts_view(request):
    # For development, we'll show all alerts
    alerts = Alert.objects.all()
    context = {
        'alerts': alerts,
    }
    return render(request, 'dashboard/alerts.html', context)

# @login_required
def keywords_view(request):
    """
    Top Keywords analytics page showing most popular keywords with detailed statistics
    """
    # Get date range parameter (default to 7 days)
    date_range = request.GET.get('date_range', '7d')
    
    # Calculate date range
    end_date = datetime.now()
    if date_range == '1d':
        start_date = end_date - timedelta(days=1)
    elif date_range == '7d':
        start_date = end_date - timedelta(days=7)
    elif date_range == '30d':
        start_date = end_date - timedelta(days=30)
    else:  # 90d
        start_date = end_date - timedelta(days=90)
    
    # Get all keywords and their usage statistics
    keywords_data = []
    
    for keyword in Keyword.objects.filter(is_active=True):
        # Count articles and posts that use this keyword
        articles_with_keyword = Article.objects.filter(
            keywords=keyword,
            scraped_at__range=(start_date, end_date)
        )
        
        posts_with_keyword = Post.objects.filter(
            keywords=keyword,
            scraped_at__range=(start_date, end_date)
        )
        
        total_mentions = articles_with_keyword.count() + posts_with_keyword.count()
        
        if total_mentions == 0:
            continue  # Skip keywords with no mentions in the date range
        
        # Get sentiment data for this keyword
        article_sentiments = ArticleSentiment.objects.filter(
            article__in=articles_with_keyword
        )
        post_sentiments = PostSentiment.objects.filter(
            post__in=posts_with_keyword
        )
        
        positive_count = (article_sentiments.filter(sentiment='positive').count() + 
                         post_sentiments.filter(sentiment='positive').count())
        negative_count = (article_sentiments.filter(sentiment='negative').count() + 
                         post_sentiments.filter(sentiment='negative').count())
        neutral_count = (article_sentiments.filter(sentiment='neutral').count() + 
                        post_sentiments.filter(sentiment='neutral').count())
        
        # Calculate sentiment percentage
        sentiment_total = positive_count + negative_count + neutral_count
        if sentiment_total > 0:
            positive_pct = round((positive_count / sentiment_total) * 100, 1)
            negative_pct = round((negative_count / sentiment_total) * 100, 1)
            neutral_pct = round((neutral_count / sentiment_total) * 100, 1)
        else:
            positive_pct = negative_pct = neutral_pct = 0
        
        # Get source distribution for this keyword
        sources_distribution = {}
        for source in Source.objects.filter(is_active=True):
            source_articles = articles_with_keyword.filter(source=source).count()
            source_posts = posts_with_keyword.filter(source=source).count()
            source_total = source_articles + source_posts
            if source_total > 0:
                sources_distribution[source.name] = source_total
        
        # Calculate trend (compare first half vs second half of period)
        mid_date = start_date + (end_date - start_date) / 2
        
        first_half_count = (
            articles_with_keyword.filter(scraped_at__lt=mid_date).count() + 
            posts_with_keyword.filter(scraped_at__lt=mid_date).count()
        )
        second_half_count = (
            articles_with_keyword.filter(scraped_at__gte=mid_date).count() + 
            posts_with_keyword.filter(scraped_at__gte=mid_date).count()
        )
        
        if first_half_count > 0:
            trend_percentage = round(((second_half_count - first_half_count) / first_half_count) * 100, 1)
        else:
            trend_percentage = 100 if second_half_count > 0 else 0
        
        if trend_percentage > 10:
            trend_direction = "increasing"
            trend_icon = "📈"
        elif trend_percentage < -10:
            trend_direction = "decreasing"
            trend_icon = "📉"
        else:
            trend_direction = "stable"
            trend_icon = "📊"
        
        keywords_data.append({
            'keyword': keyword,
            'total_mentions': total_mentions,
            'articles_count': articles_with_keyword.count(),
            'posts_count': posts_with_keyword.count(),
            'positive_count': positive_count,
            'negative_count': negative_count,
            'neutral_count': neutral_count,
            'positive_pct': positive_pct,
            'negative_pct': negative_pct,
            'neutral_pct': neutral_pct,
            'sources_distribution': sources_distribution,
            'trend_percentage': trend_percentage,
            'trend_direction': trend_direction,
            'trend_icon': trend_icon,
            'dominant_sentiment': 'positive' if positive_count > max(negative_count, neutral_count) 
                                else 'negative' if negative_count > neutral_count 
                                else 'neutral'
        })
    
    # Sort by total mentions (most popular first)
    keywords_data.sort(key=lambda x: x['total_mentions'], reverse=True)
    
    # Get top 10 for detailed display
    top_keywords = keywords_data[:10]
    
    # Prepare data for charts
    keyword_names = [kw['keyword'].term for kw in top_keywords]
    keyword_counts = [kw['total_mentions'] for kw in top_keywords]
    
    # Sentiment distribution across all top keywords
    total_positive = sum(kw['positive_count'] for kw in top_keywords)
    total_negative = sum(kw['negative_count'] for kw in top_keywords)
    total_neutral = sum(kw['neutral_count'] for kw in top_keywords)
    
    # Trending keywords (top 5 increasing)
    trending_up = [kw for kw in keywords_data if kw['trend_direction'] == 'increasing'][:5]
    trending_down = [kw for kw in keywords_data if kw['trend_direction'] == 'decreasing'][:5]
    
    # Summary statistics
    total_keywords_active = len([kw for kw in keywords_data if kw['total_mentions'] > 0])
    total_mentions_all = sum(kw['total_mentions'] for kw in keywords_data)
    avg_mentions_per_keyword = round(total_mentions_all / max(1, total_keywords_active), 1)
    
    # Most active sources across all keywords
    all_sources = {}
    for kw in keywords_data:
        for source, count in kw['sources_distribution'].items():
            all_sources[source] = all_sources.get(source, 0) + count
    
    top_sources = sorted(all_sources.items(), key=lambda x: x[1], reverse=True)[:5]
    
    # Get latest news for trending keywords
    trending_keywords_news = []
    top_trending_keywords = [kw for kw in keywords_data if kw['trend_direction'] == 'increasing'][:5]
    
    for kw in top_trending_keywords:
        # Get latest articles for this keyword (last 3 days, max 5 articles)
        recent_articles = Article.objects.filter(
            keywords=kw['keyword'],
            scraped_at__gte=end_date - timedelta(days=3),
            url__isnull=False  # Only articles with URLs
        ).exclude(url='').order_by('-scraped_at')[:5]
        
        # Get latest posts for this keyword (last 3 days, max 3 posts)
        recent_posts = Post.objects.filter(
            keywords=kw['keyword'],
            scraped_at__gte=end_date - timedelta(days=3)
        ).order_by('-scraped_at')[:3]
        
        trending_keywords_news.append({
            'keyword': kw['keyword'],
            'trend_icon': kw['trend_icon'],
            'trend_percentage': kw['trend_percentage'],
            'total_mentions': kw['total_mentions'],
            'recent_articles': recent_articles,
            'recent_posts': recent_posts,
            'dominant_sentiment': kw['dominant_sentiment']
        })
    
    # Get overall latest news (top 10 most recent articles with any tracked keywords)
    latest_news_overall = Article.objects.filter(
        keywords__isnull=False,
        scraped_at__range=(start_date, end_date),
        url__isnull=False  # Only articles with URLs
    ).exclude(url='').distinct().order_by('-scraped_at')[:10]
    
    context = {
        'keywords_data': keywords_data,
        'top_keywords': top_keywords,
        'keyword_names': json.dumps(keyword_names),
        'keyword_counts': json.dumps(keyword_counts),
        'total_positive': total_positive,
        'total_negative': total_negative,
        'total_neutral': total_neutral,
        'trending_up': trending_up,
        'trending_down': trending_down,
        'total_keywords_active': total_keywords_active,
        'total_mentions_all': total_mentions_all,
        'avg_mentions_per_keyword': avg_mentions_per_keyword,
        'top_sources': top_sources,
        'trending_keywords_news': trending_keywords_news,
        'latest_news_overall': latest_news_overall,
        'date_range': date_range,
    }
    
    return render(request, 'dashboard/keywords.html', context)

# @login_required
def security_summary_view(request):
    """
    Security Summary page with LLM-powered analysis of crawled data
    """
    from .llm_client import SecurityLLMClient
    import time
    
    # Get date range parameter (default to 1 day for fresh analysis)
    date_range = request.GET.get('date_range', '1d')
    
    # Calculate date range
    end_date = datetime.now()
    if date_range == '1d':
        start_date = end_date - timedelta(days=1)
        range_label = "Last 24 Hours"
    elif date_range == '7d':
        start_date = end_date - timedelta(days=7)
        range_label = "Last 7 Days"
    elif date_range == '30d':
        start_date = end_date - timedelta(days=30)
        range_label = "Last 30 Days"
    else:  # 90d
        start_date = end_date - timedelta(days=90)
        range_label = "Last 90 Days"
    
    # Get security-related data
    security_keywords = ['terrorism', 'attack', 'bomb', 'threat', 'violence', 'security', 
                        'militant', 'extremist', 'protest', 'riot', 'demonstration']
    
    # Filter articles and posts by security keywords and date range
    articles = Article.objects.filter(
        keywords__term__in=security_keywords,
        scraped_at__range=(start_date, end_date)
    ).distinct().order_by('-scraped_at')
    
    posts = Post.objects.filter(
        keywords__term__in=security_keywords,
        scraped_at__range=(start_date, end_date)
    ).distinct().order_by('-scraped_at')
    
    # Get trending keywords data
    trending_keywords = []
    for keyword in Keyword.objects.filter(term__in=security_keywords, is_active=True):
        # Count mentions in the date range
        keyword_articles = articles.filter(keywords=keyword)
        keyword_posts = posts.filter(keywords=keyword)
        total_mentions = keyword_articles.count() + keyword_posts.count()
        
        if total_mentions > 0:
            # Get sentiment data
            article_sentiments = ArticleSentiment.objects.filter(article__in=keyword_articles)
            post_sentiments = PostSentiment.objects.filter(post__in=keyword_posts)
            
            positive_count = (article_sentiments.filter(sentiment='positive').count() + 
                             post_sentiments.filter(sentiment='positive').count())
            negative_count = (article_sentiments.filter(sentiment='negative').count() + 
                             post_sentiments.filter(sentiment='negative').count())
            neutral_count = (article_sentiments.filter(sentiment='neutral').count() + 
                            post_sentiments.filter(sentiment='neutral').count())
            
            # Calculate trend (simplified)
            mid_date = start_date + (end_date - start_date) / 2
            first_half = (keyword_articles.filter(scraped_at__lt=mid_date).count() + 
                         keyword_posts.filter(scraped_at__lt=mid_date).count())
            second_half = (keyword_articles.filter(scraped_at__gte=mid_date).count() + 
                          keyword_posts.filter(scraped_at__gte=mid_date).count())
            
            trend_percentage = ((second_half - first_half) / max(1, first_half)) * 100 if first_half > 0 else 0
            trend_direction = 'increasing' if trend_percentage > 10 else 'decreasing' if trend_percentage < -10 else 'stable'
            
            trending_keywords.append({
                'keyword': keyword.term,
                'total_mentions': total_mentions,
                'trend_direction': trend_direction,
                'trend_percentage': round(trend_percentage, 1),
                'positive_count': positive_count,
                'negative_count': negative_count,
                'neutral_count': neutral_count,
                'dominant_sentiment': 'positive' if positive_count > max(negative_count, neutral_count) 
                                    else 'negative' if negative_count > neutral_count 
                                    else 'neutral'
            })
    
    # Sort by mentions
    trending_keywords.sort(key=lambda x: x['total_mentions'], reverse=True)
    
    # Prepare data for LLM
    articles_data = []
    for article in articles[:15]:  # Top 15 articles
        article_keywords = [{'term': kw.term} for kw in article.keywords.filter(term__in=security_keywords)]
        sentiment = 'neutral'
        try:
            article_sentiment = ArticleSentiment.objects.get(article=article)
            sentiment = article_sentiment.sentiment
        except ArticleSentiment.DoesNotExist:
            pass
        
        articles_data.append({
            'title': article.title,
            'source': article.source.name,
            'keywords': article_keywords,
            'sentiment': sentiment,
            'excerpt': article.excerpt or ''
        })
    
    posts_data = []
    for post in posts[:10]:  # Top 10 posts
        posts_data.append({
            'content': post.content,
            'source': post.source.name,
            'likes_count': post.likes_count or 0,
            'retweets_count': post.retweets_count or 0
        })
    
    # Initialize LLM client and generate analysis
    llm_client = SecurityLLMClient()
    
    # Generate different types of analysis
    analysis_start_time = time.time()
    security_summary = None
    trend_analysis = None
    incident_analysis = None
    analysis_error = None
    
    try:
        # Generate main security summary
        logger.info("Generating security summary with LLM...")
        security_summary = llm_client.generate_security_summary(
            articles_data, posts_data, trending_keywords, range_label
        )
        
        # Generate trend analysis if we have trending data
        if trending_keywords:
            trend_analysis = llm_client.generate_trend_analysis(trending_keywords)
        
        # Generate incident analysis for high-impact articles
        high_impact_articles = [a for a in articles_data if any(kw['term'] in ['attack', 'bomb', 'terrorism'] for kw in a['keywords'])]
        if high_impact_articles:
            incident_analysis = llm_client.generate_incident_analysis(high_impact_articles[:5])
            
    except Exception as e:
        logger.error(f"Error generating LLM analysis: {str(e)}")
        analysis_error = str(e)
    
    analysis_duration = time.time() - analysis_start_time
    
    # Calculate summary statistics
    total_articles = articles.count()
    total_posts = posts.count()
    
    # Get sentiment breakdown
    all_article_sentiments = ArticleSentiment.objects.filter(article__in=articles)
    all_post_sentiments = PostSentiment.objects.filter(post__in=posts)
    
    total_positive = (all_article_sentiments.filter(sentiment='positive').count() + 
                     all_post_sentiments.filter(sentiment='positive').count())
    total_negative = (all_article_sentiments.filter(sentiment='negative').count() + 
                     all_post_sentiments.filter(sentiment='negative').count())
    total_neutral = (all_article_sentiments.filter(sentiment='neutral').count() + 
                    all_post_sentiments.filter(sentiment='neutral').count())
    
    # Calculate threat level based on data
    threat_level = "Low"
    if total_negative > total_positive * 2:
        threat_level = "High" if total_articles > 20 else "Medium"
    elif total_negative > total_positive:
        threat_level = "Medium" if total_articles > 10 else "Low"
    
    # Most active sources
    source_activity = {}
    for article in articles:
        source_activity[article.source.name] = source_activity.get(article.source.name, 0) + 1
    
    top_sources = sorted(source_activity.items(), key=lambda x: x[1], reverse=True)[:5]
    
    context = {
        'security_summary': security_summary,
        'trend_analysis': trend_analysis,
        'incident_analysis': incident_analysis,
        'analysis_error': analysis_error,
        'analysis_duration': round(analysis_duration, 2),
        'trending_keywords': trending_keywords[:10],
        'total_articles': total_articles,
        'total_posts': total_posts,
        'total_positive': total_positive,
        'total_negative': total_negative,
        'total_neutral': total_neutral,
        'threat_level': threat_level,
        'top_sources': top_sources,
        'date_range': date_range,
        'range_label': range_label,
        'recent_articles': articles[:10],
        'recent_posts': posts[:5],
    }
    
    return render(request, 'dashboard/security_summary.html', context)

# @login_required
def security_summary_pdf_view(request):
    """
    Generate PDF version of the security summary
    """
    # Get the same data as the regular security summary view
    from .llm_client import SecurityLLMClient
    import time
    
    # Get date range parameter (default to 1 day for fresh analysis)
    date_range = request.GET.get('date_range', '1d')
    
    # Calculate date range
    end_date = datetime.now()
    if date_range == '1d':
        start_date = end_date - timedelta(days=1)
        range_label = "Last 24 Hours"
    elif date_range == '7d':
        start_date = end_date - timedelta(days=7)
        range_label = "Last 7 Days"
    elif date_range == '30d':
        start_date = end_date - timedelta(days=30)
        range_label = "Last 30 Days"
    else:  # 90d
        start_date = end_date - timedelta(days=90)
        range_label = "Last 90 Days"
    
    # Get security-related data (same logic as security_summary_view)
    security_keywords = ['terrorism', 'attack', 'bomb', 'threat', 'violence', 'security', 
                        'militant', 'extremist', 'protest', 'riot', 'demonstration']
    
    # Filter articles and posts by security keywords and date range
    articles = Article.objects.filter(
        keywords__term__in=security_keywords,
        scraped_at__range=(start_date, end_date)
    ).distinct().order_by('-scraped_at')
    
    posts = Post.objects.filter(
        keywords__term__in=security_keywords,
        scraped_at__range=(start_date, end_date)
    ).distinct().order_by('-scraped_at')
    
    # Get trending keywords data (simplified for PDF)
    trending_keywords = []
    for keyword in Keyword.objects.filter(term__in=security_keywords, is_active=True)[:10]:
        keyword_articles = articles.filter(keywords=keyword)
        keyword_posts = posts.filter(keywords=keyword)
        total_mentions = keyword_articles.count() + keyword_posts.count()
        
        if total_mentions > 0:
            trending_keywords.append({
                'keyword': keyword.term,
                'total_mentions': total_mentions
            })
    
    # Sort by mentions
    trending_keywords.sort(key=lambda x: x['total_mentions'], reverse=True)
    
    # Prepare data for LLM (simplified version)
    articles_data = []
    for article in articles[:10]:
        article_keywords = [{'term': kw.term} for kw in article.keywords.filter(term__in=security_keywords)]
        sentiment = 'neutral'
        try:
            article_sentiment = ArticleSentiment.objects.get(article=article)
            sentiment = article_sentiment.sentiment
        except ArticleSentiment.DoesNotExist:
            pass
        
        articles_data.append({
            'title': article.title,
            'source': article.source.name,
            'keywords': article_keywords,
            'sentiment': sentiment,
            'excerpt': article.excerpt or ''
        })
    
    posts_data = []
    for post in posts[:5]:
        posts_data.append({
            'content': post.content,
            'source': post.source.name,
            'likes_count': post.likes_count or 0,
            'retweets_count': post.retweets_count or 0
        })
    
    # Initialize LLM client and generate analysis
    llm_client = SecurityLLMClient()
    
    # Generate analysis
    analysis_start_time = time.time()
    security_summary = None
    trend_analysis = None
    incident_analysis = None
    analysis_error = None
    
    try:
        # Generate main security summary
        logger.info("Generating security summary for PDF...")
        security_summary = llm_client.generate_security_summary(
            articles_data, posts_data, trending_keywords, range_label
        )
        
        # Generate trend analysis if we have trending data
        if trending_keywords:
            trend_analysis = llm_client.generate_trend_analysis(trending_keywords)
        
        # Generate incident analysis for high-impact articles
        high_impact_articles = [a for a in articles_data if any(kw['term'] in ['attack', 'bomb', 'terrorism'] for kw in a['keywords'])]
        if high_impact_articles:
            incident_analysis = llm_client.generate_incident_analysis(high_impact_articles[:5])
            
    except Exception as e:
        logger.error(f"Error generating LLM analysis for PDF: {str(e)}")
        analysis_error = str(e)
    
    analysis_duration = time.time() - analysis_start_time
    
    # Calculate summary statistics
    total_articles = articles.count()
    total_posts = posts.count()
    
    # Get sentiment breakdown
    all_article_sentiments = ArticleSentiment.objects.filter(article__in=articles)
    all_post_sentiments = PostSentiment.objects.filter(post__in=posts)
    
    total_positive = (all_article_sentiments.filter(sentiment='positive').count() + 
                     all_post_sentiments.filter(sentiment='positive').count())
    total_negative = (all_article_sentiments.filter(sentiment='negative').count() + 
                     all_post_sentiments.filter(sentiment='negative').count())
    total_neutral = (all_article_sentiments.filter(sentiment='neutral').count() + 
                    all_post_sentiments.filter(sentiment='neutral').count())
    
    # Calculate threat level based on data
    threat_level = "Low"
    if total_negative > total_positive * 2:
        threat_level = "High" if total_articles > 20 else "Medium"
    elif total_negative > total_positive:
        threat_level = "Medium" if total_articles > 10 else "Low"
    
    # Most active sources
    source_activity = {}
    for article in articles:
        source_activity[article.source.name] = source_activity.get(article.source.name, 0) + 1
    
    top_sources = sorted(source_activity.items(), key=lambda x: x[1], reverse=True)[:5]
    
    # Generate PDF
    context = {
        'security_summary': security_summary,
        'trend_analysis': trend_analysis,
        'incident_analysis': incident_analysis,
        'analysis_error': analysis_error,
        'analysis_duration': round(analysis_duration, 2),
        'trending_keywords': trending_keywords[:10],
        'total_articles': total_articles,
        'total_posts': total_posts,
        'total_positive': total_positive,
        'total_negative': total_negative,
        'total_neutral': total_neutral,
        'threat_level': threat_level,
        'top_sources': top_sources,
        'date_range': date_range,
        'range_label': range_label,
        'recent_articles': articles[:10],
        'generated_date': datetime.now().strftime('%B %d, %Y at %I:%M %p'),
    }
    
    # Render HTML for PDF
    html_string = render_to_string('dashboard/security_summary_pdf.html', context)
    
    # Generate PDF
    try:
        logger.info("Starting PDF generation...")
        
        # Create PDF using WeasyPrint
        pdf_bytes = HTML(string=html_string).write_pdf()
        
        if pdf_bytes is None:
            raise Exception("PDF generation returned None")
        
        logger.info(f"PDF generated successfully, size: {len(pdf_bytes)} bytes")
        
        # Create HTTP response
        response = HttpResponse(pdf_bytes, content_type='application/pdf')
        filename = f"security_summary_{date_range}_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        return response
        
    except Exception as e:
        logger.error(f"Error generating PDF: {str(e)}")
        import traceback
        logger.error(f"Full traceback: {traceback.format_exc()}")
        
        # Return error response
        error_msg = f"Error generating PDF: {str(e)}"
        return HttpResponse(error_msg.encode('utf-8'), content_type='text/plain; charset=utf-8', status=500)


# @login_required
def threat_classification_view(request):
    """Threat Classification page for man guarding services"""
    date_range = '7d'
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)

    # Get all articles
    articles = Article.objects.filter(scraped_at__range=(start_date, end_date))

    # Define threat categories based on keywords
    threat_categories = {
        'Pencurian & Perampokan': ['pencurian', 'perampokan', 'maling', 'pembobolan', 'theft', 'robbery', 'burglary'],
        'Kerusuhan & Demo': ['kerusuhan', 'demo', 'unjuk rasa', 'demonstrasi', 'mogok kerja', 'riot', 'protest', 'strike'],
        'Terorisme & Ancaman Bom': ['terorisme', 'bom', 'ancaman bom', 'benda mencurigakan', 'terrorism', 'bomb threat'],
        'Pengrusakan & Vandalisme': ['pengrusakan', 'vandalisme', 'sabotase', 'pembakaran', 'vandalism', 'sabotage'],
        'Kejahatan Lainnya': ['penculikan', 'pencopetan', 'penjambretan', 'penodongan', 'kriminal'],
        'Kecelakaan & Darurat': ['kecelakaan kerja', 'kebakaran', 'kebocoran gas', 'bahaya kimia', 'darurat medis'],
    }

    # Calculate threat counts
    threat_data = []
    total_threats = 0

    for category, keywords in threat_categories.items():
        # Count articles matching this category's keywords
        count = 0
        category_articles = []

        for article in articles:
            article_keywords = [kw.term.lower() for kw in article.keywords.all()]
            if any(kw in article_keywords for kw in keywords):
                count += 1
                if len(category_articles) < 5:  # Keep top 5 for display
                    category_articles.append({
                        'title': article.title,
                        'source': article.source.name,
                        'published_at': article.published_at,
                        'url': article.url
                    })

        if count > 0:
            total_threats += count
            threat_data.append({
                'category': category,
                'count': count,
                'percentage': 0,  # Will calculate after total
                'recent_incidents': category_articles,
                'severity': 'Tinggi' if count > 10 else 'Sedang' if count > 5 else 'Rendah'
            })

    # Calculate percentages
    for threat in threat_data:
        if total_threats > 0:
            threat['percentage'] = round((threat['count'] / total_threats) * 100, 1)

    # Sort by count
    threat_data = sorted(threat_data, key=lambda x: x['count'], reverse=True)

    # Regional analysis - extract city names from articles
    regions = ['jakarta', 'surabaya', 'bandung', 'semarang', 'medan', 'bekasi', 'tangerang', 'bogor', 'cikarang']
    regional_threats = []

    for region in regions:
        region_count = 0
        for article in articles:
            if region in article.title.lower() or region in article.content.lower():
                region_count += 1

        if region_count > 0:
            regional_threats.append({
                'region': region.capitalize(),
                'count': region_count,
                'status': 'Siaga' if region_count > 10 else 'Waspada' if region_count > 5 else 'Normal'
            })

    regional_threats = sorted(regional_threats, key=lambda x: x['count'], reverse=True)

    context = {
        'threat_data': threat_data,
        'total_threats': total_threats,
        'regional_threats': regional_threats,
        'date_range': date_range,
        'total_articles': articles.count(),
    }

    return render(request, 'dashboard/threat_classification.html', context)


# @login_required
def regional_security_view(request):
    """Regional Security Status page for man guarding services"""
    date_range = '7d'
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)

    # Get all articles
    articles = Article.objects.filter(scraped_at__range=(start_date, end_date))

    # Define regions to monitor
    regions_config = {
        'Jakarta': {
            'keywords': ['jakarta', 'dki jakarta', 'jakarta pusat', 'jakarta selatan', 'jakarta utara', 'jakarta barat', 'jakarta timur'],
            'areas': ['Perkantoran CBD', 'Kawasan Industri', 'Perumahan', 'Retail & Mall']
        },
        'Bekasi': {
            'keywords': ['bekasi', 'kota bekasi', 'bekasi timur', 'bekasi barat'],
            'areas': ['Kawasan Industri MM2100', 'Kawasan Industri EJIP', 'Perkantoran', 'Perumahan']
        },
        'Cikarang': {
            'keywords': ['cikarang', 'delta silicon', 'jababeka', 'hyundai'],
            'areas': ['Kawasan Industri Jababeka', 'Kawasan Industri Delta Silicon', 'Kawasan Industri MM2100', 'Greenland']
        },
        'Tangerang': {
            'keywords': ['tangerang', 'bsd', 'gading serpong', 'bintaro'],
            'areas': ['BSD City', 'Gading Serpong', 'Kawasan Industri', 'Bintaro']
        },
        'Surabaya': {
            'keywords': ['surabaya', 'sidoarjo', 'gresik'],
            'areas': ['SIER (Surabaya Industrial Estate)', 'Kawasan Industri Rungkut', 'CBD Surabaya', 'Pelabuhan Tanjung Perak']
        },
        'Bandung': {
            'keywords': ['bandung', 'cimahi', 'bandung barat'],
            'areas': ['Kawasan Industri Majalaya', 'Perkantoran Kota', 'Kawasan Pendidikan', 'Retail & Wisata']
        },
    }

    regional_data = []

    for region_name, config in regions_config.items():
        # Count articles mentioning this region
        region_articles = []
        threat_count = 0
        threat_types = {'pencurian': 0, 'demo': 0, 'kerusuhan': 0, 'kecelakaan': 0, 'lainnya': 0}

        for article in articles:
            content_lower = (article.title + ' ' + article.content).lower()
            if any(kw in content_lower for kw in config['keywords']):
                region_articles.append(article)
                threat_count += 1

                # Categorize threat type
                article_keywords = [kw.term.lower() for kw in article.keywords.all()]
                if any(k in article_keywords for k in ['pencurian', 'perampokan', 'maling']):
                    threat_types['pencurian'] += 1
                elif any(k in article_keywords for k in ['demo', 'unjuk rasa', 'mogok kerja']):
                    threat_types['demo'] += 1
                elif any(k in article_keywords for k in ['kerusuhan', 'ricuh', 'bentrok']):
                    threat_types['kerusuhan'] += 1
                elif any(k in article_keywords for k in ['kecelakaan kerja', 'kebakaran']):
                    threat_types['kecelakaan'] += 1
                else:
                    threat_types['lainnya'] += 1

        # Determine security status
        if threat_count >= 15:
            status = 'Kritis'
            status_color = 'danger'
        elif threat_count >= 10:
            status = 'Siaga'
            status_color = 'warning'
        elif threat_count >= 5:
            status = 'Waspada'
            status_color = 'info'
        else:
            status = 'Normal'
            status_color = 'success'

        # Get top threat type
        top_threat = max(threat_types, key=threat_types.get) if threat_count > 0 else 'Tidak ada'

        # Recent incidents (top 3)
        recent_incidents = []
        for article in region_articles[:3]:
            recent_incidents.append({
                'title': article.title[:100],
                'source': article.source.name,
                'published_at': article.published_at,
            })

        regional_data.append({
            'region': region_name,
            'status': status,
            'status_color': status_color,
            'threat_count': threat_count,
            'threat_types': threat_types,
            'top_threat': top_threat.capitalize(),
            'areas': config['areas'],
            'recent_incidents': recent_incidents,
        })

    # Sort by threat count (highest first)
    regional_data = sorted(regional_data, key=lambda x: x['threat_count'], reverse=True)

    context = {
        'regional_data': regional_data,
        'date_range': date_range,
        'total_regions': len(regional_data),
    }

    return render(request, 'dashboard/regional_security.html', context)