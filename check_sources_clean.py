import os
import django

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'osint_dashboard.settings')
django.setup()

from scraper.models import Source

def check_sources():
    # Check all configured sources
    print("Checking all sources...")
    
    sources = Source.objects.all()
    for source in sources:
        print("\nSource: {}".format(source.name))
        print("  Type: {}".format(source.source_type))
        print("  URL: {}".format(source.url))
        print("  Active: {}".format(source.is_active))

if __name__ == '__main__':
    check_sources()