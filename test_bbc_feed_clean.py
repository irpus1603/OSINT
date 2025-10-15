import os
import django

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'osint_dashboard.settings')
django.setup()

import feedparser
import requests

def test_bbc_feed():
    # Test BBC feed access
    url = "https://feeds.bbci.co.uk/news/world/rss.xml"
    print("Testing BBC feed access: {}".format(url))
    
    try:
        # Test direct HTTP request
        print("Making direct HTTP request...")
        response = requests.get(url, timeout=30)
        print("Status code: {}".format(response.status_code))
        print("Content length: {}".format(len(response.text)))
        print("Content preview: {}...".format(response.text[:200]))
        
        # Test feedparser
        print("\nParsing with feedparser...")
        parsed = feedparser.parse(url)
        print("Bozo flag: {}".format(parsed.bozo))
        print("Feed title: {}".format(getattr(parsed.feed, 'title', 'Unknown')))
        print("Entries count: {}".format(len(parsed.entries)))
        
        if parsed.entries:
            print("First entry title: {}".format(getattr(parsed.entries[0], 'title', 'No title')))
            print("First entry link: {}".format(getattr(parsed.entries[0], 'link', 'No link')))
        else:
            print("No entries found")
            
        # Check for errors
        if hasattr(parsed, 'bozo_exception'):
            print("Bozo exception: {}".format(parsed.bozo_exception))
            
    except Exception as e:
        print("Error: {}".format(e))

if __name__ == '__main__':
    test_bbc_feed()