import os
import django

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'osint_dashboard.settings')
django.setup()

import feedparser
from scraper.tasks import scrape_news_source, match_keywords
from scraper.models import Source, Keyword

def test_rss_feed():
    """Test RSS feed parsing and keyword matching"""
    print("Testing RSS feed parsing...")
    
    # Get the first news source
    news_source = Source.objects.filter(source_type='news', is_active=True).first()
    
    if news_source:
        print("Source: {}".format(news_source.name))
        print("URL: {}".format(news_source.url))
        
        # Parse RSS feed
        print("Parsing RSS feed...")
        parsed = feedparser.parse(news_source.url)
        print("Feed parsed. Bozo: {}".format(parsed.bozo))
        print("Entries found: {}".format(len(parsed.entries)))
        
        # Get active keywords
        keywords = Keyword.objects.filter(is_active=True)
        print("Active keywords: {}".format([kw.term for kw in keywords]))
        
        # Check first few entries
        for i, entry in enumerate(parsed.entries[:5]):
            print("\nEntry {}:".format(i+1))
            title = (entry.get("title") or "").strip()
            summary = (entry.get("summary") or entry.get("description") or "").strip()
            print("  Title: {}".format(title))
            print("  Summary: {}...".format(summary[:100]))
            
            # Test keyword matching
            base_text = "{}\n{}".format(title, summary)
            hits = match_keywords(base_text)
            print("  Keyword matches: {}".format(hits))
            
            if hits:
                print("  MATCHED! Keywords: {}".format(hits))
    else:
        print("No active news sources found")

if __name__ == '__main__':
    test_rss_feed()