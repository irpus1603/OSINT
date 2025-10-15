from django.utils import timezone
from .models import Source, Keyword, Article, Post
from scraper.tasks import scrape_news_source, scrape_social_media_source

class ScraperService:
    """Service class for handling scraping operations"""
    
    @staticmethod
    def scrape_source(source_id):
        """Scrape a specific source by ID"""
        try:
            source = Source.objects.get(id=source_id, is_active=True)
        except Source.DoesNotExist:
            raise ValueError(f"Source with ID {source_id} not found or inactive")
        
        if source.source_type == 'news':
            return scrape_news_source(source_id)
        elif source.source_type == 'social':
            return scrape_social_media_source(source_id)
        else:
            raise ValueError(f"Unsupported source type: {source.source_type}")
    
    @staticmethod
    def scrape_all_sources():
        """Scrape all active sources"""
        active_sources = Source.objects.filter(is_active=True)
        results = []
        
        for source in active_sources:
            try:
                result = ScraperService.scrape_source(source.id)
                results.append({
                    'source': source.name,
                    'result': result,
                    'status': 'success'
                })
            except Exception as e:
                results.append({
                    'source': source.name,
                    'result': str(e),
                    'status': 'error'
                })
        
        return results
    
    @staticmethod
    def get_scraping_stats():
        """Get statistics about scraped content"""
        stats = {
            'total_articles': Article.objects.count(),
            'total_posts': Post.objects.count(),
            'articles_today': Article.objects.filter(
                scraped_at__date=timezone.now().date()
            ).count(),
            'posts_today': Post.objects.filter(
                scraped_at__date=timezone.now().date()
            ).count(),
            'active_sources': Source.objects.filter(is_active=True).count(),
            'total_keywords': Keyword.objects.filter(is_active=True).count(),
        }
        return stats