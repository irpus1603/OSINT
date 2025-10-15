from django.core.management.base import BaseCommand
from scraper.services import ScraperService

class Command(BaseCommand):
    help = 'Scrape all active sources'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--source-id',
            type=int,
            help='ID of specific source to scrape',
        )
        parser.add_argument(
            '--stats',
            action='store_true',
            help='Show scraping statistics',
        )
    
    def handle(self, *args, **options):
        if options['stats']:
            stats = ScraperService.get_scraping_stats()
            self.stdout.write(
                self.style.SUCCESS(
                    f"Scraping Statistics:\\n"
                    f"  Total Articles: {stats['total_articles']}\\n"
                    f"  Total Posts: {stats['total_posts']}\\n"
                    f"  Articles Today: {stats['articles_today']}\\n"
                    f"  Posts Today: {stats['posts_today']}\\n"
                    f"  Active Sources: {stats['active_sources']}\\n"
                    f"  Active Keywords: {stats['total_keywords']}\\n"
                )
            )
            return
        
        if options['source_id']:
            try:
                result = ScraperService.scrape_source(options['source_id'])
                self.stdout.write(
                    self.style.SUCCESS(f'Successfully scraped source: {result}')
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Error scraping source: {e}')
                )
        else:
            results = ScraperService.scrape_all_sources()
            for result in results:
                if result['status'] == 'success':
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"Successfully scraped {result['source']}: {result['result']}"
                        )
                    )
                else:
                    self.stdout.write(
                        self.style.ERROR(
                            f"Error scraping {result['source']}: {result['result']}"
                        )
                    )