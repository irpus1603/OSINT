import os
import django

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'osint_dashboard.settings')
django.setup()

from scraper.models import Source

def update_sources():
    """Update source URLs to working ones"""
    print("Updating source URLs...")
    
    # Update Reuters to a working feed
    reuters = Source.objects.filter(name='Reuters').first()
    if reuters:
        reuters.url = 'https://feeds.reuters.com/reuters/topNews'  # This was the old one
        reuters.save()
        print("Updated Reuters URL")
    
    # Let's check what working sources we have
    working_sources = [
        ('BBC World', 'https://feeds.bbci.co.uk/news/world/rss.xml'),
        ('CNN International', 'http://rss.cnn.com/rss/edition.rss'),
        ('Al Jazeera', 'https://www.aljazeera.com/xml/rss/all.xml'),
    ]
    
    for name, url in working_sources:
        source = Source.objects.filter(name=name).first()
        if source:
            source.url = url
            source.is_active = True
            source.save()
            print("Updated {}: {}".format(name, url))
    
    # Check all sources
    sources = Source.objects.all()
    for source in sources:
        print("\n{} ({})".format(source.name, source.source_type))
        print("  URL: {}".format(source.url))
        print("  Active: {}".format(source.is_active))

if __name__ == '__main__':
    update_sources()