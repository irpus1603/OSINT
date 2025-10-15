import os
import django

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'osint_dashboard.settings')
django.setup()

from scraper.models import Source

def fix_broken_sources():
    # Fix broken source URLs with working alternatives
    print("Fixing broken source URLs...")
    
    # Update Reuters to a working alternative or BBC (both work)
    reuters = Source.objects.filter(name='Reuters').first()
    if reuters:
        # Temporarily use BBC feed since Reuters is broken
        old_url = reuters.url
        reuters.url = 'https://feeds.bbci.co.uk/news/world/rss.xml'  # Working BBC feed
        reuters.save()
        print("Fixed Reuters: {} -> {}".format(old_url, reuters.url))
    
    # Update Jakarta Post to a working alternative
    jakarta_post = Source.objects.filter(name='The Jakarta Post').first()
    if jakarta_post:
        # Use a working Indonesian news source
        old_url = jakarta_post.url
        jakarta_post.url = 'https://www.antaranews.com/rss/terkini.xml'  # Working Antara feed
        jakarta_post.save()
        print("Fixed Jakarta Post: {} -> {}".format(old_url, jakarta_post.url))
    
    # Twitter should use API, but for now let's note that
    twitter = Source.objects.filter(name='Twitter').first()
    if twitter:
        print("Twitter source needs API configuration for proper functionality")
        print("Current URL: {}".format(twitter.url))
    
    # Test all sources
    print("\nTesting all sources...")
    sources = Source.objects.filter(is_active=True)
    for source in sources:
        print("\n{} ({})".format(source.name, source.source_type))
        print("  URL: {}".format(source.url))
        
        # Quick test
        import requests
        try:
            response = requests.head(source.url, timeout=5)
            status = "OK" if response.status_code == 200 else "Error ({})".format(response.status_code)
            print("  Status: {}".format(status))
        except Exception as e:
            print("  Status: Error - {}".format(str(e)[:50]))

if __name__ == '__main__':
    fix_broken_sources()