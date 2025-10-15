import os
import django

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'osint_dashboard.settings')
django.setup()

from scraper.models import Article, Source

def check_bbc_articles():
    # Check BBC articles in database
    print("Checking BBC articles in database...")
    
    bbc_source = Source.objects.filter(name='BBC World', is_active=True).first()
    
    if bbc_source:
        articles = Article.objects.filter(source=bbc_source).order_by('-scraped_at')
        print("BBC articles count: {}".format(articles.count()))
        
        print("\nRecent BBC articles:")
        for i, article in enumerate(articles[:10]):
            print("{}. {} ({})".format(i+1, article.title, article.scraped_at))
            
        # Check if our matching articles are in there
        print("\nChecking for specific matching articles:")
        matching_titles = [
            "Six Israelis killed by Palestinian gunmen at Jerusalem bus stop",
            "At least 19 dead in Nepal after Gen Z protests at corruption and social media ban"
        ]
        
        for title in matching_titles:
            exists = articles.filter(title__icontains=title.split()[0]).exists()
            print("  '{}': {}".format(title, "Exists" if exists else "Not found"))
    else:
        print("BBC source not found")

if __name__ == '__main__':
    check_bbc_articles()