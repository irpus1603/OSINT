from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from scheduler.models import CrawlTask
from scraper.models import Source

class Command(BaseCommand):
    help = 'Initialize default crawl tasks'
    
    def handle(self, *args, **options):
        # Get active sources
        news_sources = Source.objects.filter(source_type='news', is_active=True)
        social_sources = Source.objects.filter(source_type='social', is_active=True)
        
        if not news_sources.exists():
            self.stdout.write(
                self.style.WARNING('No active news sources found. Please create some sources first.')
            )
            return
            
        if not social_sources.exists():
            self.stdout.write(
                self.style.WARNING('No active social media sources found. Please create some sources first.')
            )
            return
        
        # Create or update default tasks
        tasks_config = [
            {
                'name': 'Hourly News Crawl',
                'source': news_sources.first(),
                'frequency': 'hourly',
                'description': 'Crawl news sources every hour'
            },
            {
                'name': 'Daily Social Media Crawl',
                'source': social_sources.first(),
                'frequency': 'daily',
                'description': 'Crawl social media sources daily'
            },
            {
                'name': 'Weekly Security News Crawl',
                'source': news_sources.first(),
                'frequency': 'weekly',
                'description': 'Comprehensive weekly security news crawl'
            }
        ]
        
        created_count = 0
        updated_count = 0
        
        for config in tasks_config:
            task, created = CrawlTask.objects.get_or_create(
                name=config['name'],
                defaults={
                    'source': config['source'],
                    'frequency': config['frequency'],
                    'is_active': True,
                    'next_run': self.calculate_next_run(config['frequency']),
                    'status': 'pending'
                }
            )
            
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f"Created task: {task.name}")
                )
            else:
                # Update existing task if needed
                if not task.next_run:
                    task.next_run = self.calculate_next_run(config['frequency'])
                    task.save()
                    updated_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(f"Updated task: {task.name}")
                    )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully initialized {created_count} new tasks and updated {updated_count} existing tasks.'
            )
        )
    
    def calculate_next_run(self, frequency):
        """Calculate next run time based on frequency"""
        now = timezone.now()
        if frequency == 'hourly':
            return now + timedelta(hours=1)
        elif frequency == 'daily':
            return now + timedelta(days=1)
        elif frequency == 'weekly':
            return now + timedelta(weeks=1)
        else:
            return now + timedelta(days=1)