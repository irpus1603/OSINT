import os
import django

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'osint_dashboard.settings')
django.setup()

import feedparser
from scraper.tasks import scrape_news_source, match_keywords
from scraper.models import Source, Keyword

def test_bbc_scraping():
    # Test BBC scraping with keyword matching
    print("Testing BBC scraping...")
    
    # Get BBC source
    bbc_source = Source.objects.filter(name='BBC World', is_active=True).first()
    
    if bbc_source:
        print("Source: {}".format(bbc_source.name))
        print("URL: {}".format(bbc_source.url))
        
        # Parse RSS feed
        print("Parsing RSS feed...")
        parsed = feedparser.parse(bbc_source.url)
        print("Entries found: {}".format(len(parsed.entries)))
        
        # Get active keywords
        keywords = Keyword.objects.filter(is_active=True)
        print("Active keywords: {}".format([kw.term for kw in keywords]))
        
        # Check first few entries for keyword matches
        matches_found = 0
        for i, entry in enumerate(parsed.entries[:10]):
            title = (entry.get("title") or "").strip()
            summary = (entry.get("summary") or entry.get("description") or "").strip()
            
            # Test keyword matching
            base_text = "{}\n{}".format(title, summary)
            hits = match_keywords(base_text)
            
            if hits:
                print("\nMATCH FOUND in entry {}:".format(i+1))
                print("  Title: {}".format(title))
                print("  Keywords matched: {}".format(hits))
                matches_found += 1
                
        print("\nTotal matches found: {}".format(matches_found))
        
        # Now test the actual scraping task
        print("\nTesting actual scraping task...")
        result = scrape_news_source(bbc_source.id)
        print("Scraping result: {}".format(result))
    else:
        print("BBC source not found")

if __name__ == '__main__':
    test_bbc_scraping()