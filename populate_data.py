import os
import django

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'osint_dashboard.settings')
django.setup()

from scraper.models import Source, Keyword

# Create sample sources
sources_data = [
    {
        'name': 'Reuters',
        'url': 'https://feeds.reuters.com/reuters/topNews',
        'source_type': 'news',
        'is_active': True
    },
    {
        'name': 'BBC World',
        'url': 'https://feeds.bbci.co.uk/news/world/rss.xml',
        'source_type': 'news',
        'is_active': True
    },
    {
        'name': 'CNN International',
        'url': 'https://rss.cnn.com/rss/edition_world.rss',
        'source_type': 'news',
        'is_active': True
    },
    {
        'name': 'Al Jazeera',
        'url': 'https://www.aljazeera.com/xml/rss/all.xml',
        'source_type': 'news',
        'is_active': True
    },
    {
        'name': 'AP News',
        'url': 'https://apnews.com/apf-topnews?output=rss',
        'source_type': 'news',
        'is_active': True
    },
    {
        'name': 'Kompas',
        'url': 'https://www.kompas.com/kompascom/feed',
        'source_type': 'news',
        'is_active': True
    },
    {
        'name': 'Detikcom',
        'url': 'https://rss.detik.com/index.php/detikcom',
        'source_type': 'news',
        'is_active': True
    },
    {
        'name': 'CNN Indonesia',
        'url': 'https://www.cnnindonesia.com/nasional/rss',
        'source_type': 'news',
        'is_active': True
    },
    {
        'name': 'Antara News',
        'url': 'https://www.antaranews.com/rss/terkini.xml',
        'source_type': 'news',
        'is_active': True
    },
    {
        'name': 'The Jakarta Post',
        'url': 'https://www.thejakartapost.com/rss',
        'source_type': 'news',
        'is_active': True
    },
    {
        'name': 'Twitter',
        'url': 'https://twitter.com',
        'source_type': 'social',
        'is_active': True
    }
]

# Create sample keywords
keywords_data = [
    # English keywords
    'terrorism', 'bomb', 'explosion', 'attack', 'militant', 'insurgent', 
    'hostage', 'shooting', 'threat', 'security', 'riot', 'protest', 
    'demonstration', 'extremist', 'radicalization', 'cyber attack',
    
    # Indonesian keywords
    'terorisme', 'bom', 'ledakan', 'serangan', 'milisi', 'pemberontak',
    'sandera', 'penembakan', 'ancaman', 'keamanan', 'kerusuhan', 'demo',
    'unjuk rasa', 'penculikan', 'ekstremis', 'radikalisasi'
]

def create_sources():
    for source_data in sources_data:
        source, created = Source.objects.get_or_create(
            url=source_data['url'],
            defaults=source_data
        )
        if created:
            print(f"Created source: {source.name}")
        else:
            print(f"Source already exists: {source.name}")

def create_keywords():
    for keyword_term in keywords_data:
        keyword, created = Keyword.objects.get_or_create(
            term=keyword_term.lower(),
            defaults={'is_active': True}
        )
        if created:
            print(f"Created keyword: {keyword.term}")
        else:
            print(f"Keyword already exists: {keyword.term}")

if __name__ == '__main__':
    print("Creating sources...")
    create_sources()
    
    print("\nCreating keywords...")
    create_keywords()
    
    print("\nDone!")