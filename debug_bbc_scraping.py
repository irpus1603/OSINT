import os
import django

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'osint_dashboard.settings')
django.setup()

import feedparser
from scraper.tasks import scrape_news_source, match_keywords
from scraper.models import Source, Keyword, Article

def debug_bbc_scraping():
    # Debug BBC scraping with detailed logging
    print("Debugging BBC scraping...")
    
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
        print("Active keywords count: {}".format(keywords.count()))
        
        # Check first few entries for keyword matches
        matches_found = 0
        articles_before = Article.objects.count()
        print("Articles before scraping: {}".format(articles_before))
        
        for i, entry in enumerate(parsed.entries[:10]):
            url = entry.get("link") or ""
            title = (entry.get("title") or "").strip()
            summary = (entry.get("summary") or entry.get("description") or "").strip()
            
            if not url:
                continue
                
            print("\nEntry {}:".format(i+1))
            print("  Title: {}".format(title))
            print("  URL: {}".format(url))
            
            # Test keyword matching
            base_text = "{}\n{}".format(title, summary)
            hits = match_keywords(base_text)
            
            print("  Keywords matched: {}".format(hits))
            
            if hits:
                print("  MATCH FOUND!")
                matches_found += 1
                
                # Check if article already exists
                if Article.objects.filter(url=url).exists():
                    print("  Article already exists in database")
                else:
                    print("  Article would be new")
        
        print("\nTotal matches found: {}".format(matches_found))
        
        # Now test the actual scraping task
        print("\nTesting actual scraping task...")
        result = scrape_news_source(bbc_source.id)
        print("Scraping result: {}".format(result))
        
        articles_after = Article.objects.count()
        print("Articles after scraping: {}".format(articles_after))
        print("Net articles created: {}".format(articles_after - articles_before))
        
        # Show recently created articles
        recent_articles = Article.objects.order_by('-scraped_at')[:5]
        print("\nRecently scraped articles:")
        for article in recent_articles:
            print("  - {} ({})".format(article.title, article.source.name))
    else:
        print("BBC source not found")

if __name__ == '__main__':
    debug_bbc_scraping()