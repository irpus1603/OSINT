import os
import django

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'osint_dashboard.settings')
django.setup()

import feedparser
from scraper.tasks import scrape_news_source, match_keywords
from scraper.models import Source, Keyword

def test_rss_feed():
    \"\"\"Test RSS feed parsing and keyword matching\"\"\"
    print(\"Testing RSS feed parsing...\")
    
    # Get the first news source
    news_source = Source.objects.filter(source_type='news', is_active=True).first()
    
    if news_source:
        print(f\"Source: {news_source.name}\")
        print(f\"URL: {news_source.url}\")
        
        # Parse RSS feed
        print(\"Parsing RSS feed...\")
        parsed = feedparser.parse(news_source.url)
        print(f\"Feed parsed. Bozo: {parsed.bozo}\")
        print(f\"Entries found: {len(parsed.entries)}\")
        
        # Get active keywords
        keywords = Keyword.objects.filter(is_active=True)
        print(f\"Active keywords: {[kw.term for kw in keywords]}\")
        
        # Check first few entries
        for i, entry in enumerate(parsed.entries[:5]):
            print(f\"\\nEntry {i+1}:\")
            title = (entry.get(\"title\") or \"\").strip()
            summary = (entry.get(\"summary\") or entry.get(\"description\") or \"\").strip()
            print(f\"  Title: {title}\")
            print(f\"  Summary: {summary[:100]}...\")
            
            # Test keyword matching
            base_text = f\"{title}\\n{summary}\"
            hits = match_keywords(base_text)
            print(f\"  Keyword matches: {hits}\")
            
            if hits:
                print(f\"  MATCHED! Keywords: {hits}\")
    else:
        print(\"No active news sources found\")

if __name__ == '__main__':
    test_rss_feed()