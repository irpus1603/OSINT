import os
import django

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'osint_dashboard.settings')
django.setup()

# Test importing the tasks
try:
    from scraper.tasks import scrape_news_source, scrape_social_media_source, run_scheduled_scraping
    print("All tasks imported successfully!")
except Exception as e:
    print(f"Error importing tasks: {e}")