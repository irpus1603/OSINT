#!/usr/bin/env python
"""
Update news sources for man guarding services focus - Indonesian security news
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'osint_dashboard.settings')
django.setup()

from scraper.models import Source

# Indonesian news sources focused on security, crime, and local news
INDONESIAN_SECURITY_SOURCES = [
    # Major Indonesian news portals
    {
        'name': 'Detik News',
        'url': 'https://rss.detik.com/index.php/detikcom',
        'source_type': 'news'
    },
    {
        'name': 'Kompas',
        'url': 'https://www.kompas.com/kompascom/feed',
        'source_type': 'news'
    },
    {
        'name': 'Tempo',
        'url': 'https://www.tempo.co/rss/metro',
        'source_type': 'news'
    },
    {
        'name': 'CNN Indonesia - Nasional',
        'url': 'https://www.cnnindonesia.com/nasional/rss',
        'source_type': 'news'
    },
    {
        'name': 'Antara News',
        'url': 'https://www.antaranews.com/rss/terkini.xml',
        'source_type': 'news'
    },
    {
        'name': 'Tribun News',
        'url': 'https://www.tribunnews.com/rss',
        'source_type': 'news'
    },
    {
        'name': 'Sindonews',
        'url': 'https://www.sindonews.com/feed',
        'source_type': 'news'
    },
    {
        'name': 'Liputan6',
        'url': 'https://www.liputan6.com/news/feed',
        'source_type': 'news'
    },
    {
        'name': 'VIVA News',
        'url': 'https://www.viva.co.id/rss/all',
        'source_type': 'news'
    },
    {
        'name': 'Republika',
        'url': 'https://www.republika.co.id/rss/',
        'source_type': 'news'
    },
    {
        'name': 'Bisnis Indonesia',
        'url': 'https://ekonomi.bisnis.com/index.xml',
        'source_type': 'news'
    },
    # Regional news - Jakarta
    {
        'name': 'Jakarta Tribune',
        'url': 'https://jakarta.tribunnews.com/rss',
        'source_type': 'news'
    },
    {
        'name': 'Berita Jakarta',
        'url': 'https://www.beritajakarta.id/rss',
        'source_type': 'news'
    },
    # Regional news - Surabaya
    {
        'name': 'Surya Surabaya',
        'url': 'https://surabaya.tribunnews.com/rss',
        'source_type': 'news'
    },
    # Regional news - Bandung
    {
        'name': 'Tribun Jabar',
        'url': 'https://jabar.tribunnews.com/rss',
        'source_type': 'news'
    },
    # Police and law enforcement
    {
        'name': 'Kompas - Hukum Kriminal',
        'url': 'https://nasional.kompas.com/rss/hukum',
        'source_type': 'news'
    },
    # English sources for international context
    {
        'name': 'The Jakarta Post',
        'url': 'https://www.thejakartapost.com/rss',
        'source_type': 'news'
    },
    {
        'name': 'Jakarta Globe',
        'url': 'https://jakartaglobe.id/feed',
        'source_type': 'news'
    },
    # Social media monitoring
    {
        'name': 'Twitter/X Indonesia',
        'url': 'https://twitter.com',
        'source_type': 'social'
    },
]

def update_sources():
    """Update news sources in database"""

    print("=" * 70)
    print("UPDATING NEWS SOURCES FOR MAN GUARDING SERVICES")
    print("=" * 70)

    # Deactivate all existing sources
    print("\n1. Deactivating existing sources...")
    old_count = Source.objects.filter(is_active=True).update(is_active=False)
    print(f"   Deactivated {old_count} existing sources")

    # Add/update Indonesian security sources
    print("\n2. Adding Indonesian security news sources...")
    created_count = 0
    updated_count = 0

    for source_data in INDONESIAN_SECURITY_SOURCES:
        source, created = Source.objects.get_or_create(
            url=source_data['url'],
            defaults={
                'name': source_data['name'],
                'source_type': source_data['source_type'],
                'is_active': True
            }
        )

        if created:
            created_count += 1
            print(f"   ✓ Created: {source_data['name']} [{source_data['source_type']}]")
        else:
            source.name = source_data['name']
            source.source_type = source_data['source_type']
            source.is_active = True
            source.save()
            updated_count += 1
            print(f"   ✓ Updated: {source_data['name']} [{source_data['source_type']}]")

    print(f"\n3. Summary:")
    print(f"   - New sources created: {created_count}")
    print(f"   - Sources reactivated/updated: {updated_count}")
    print(f"   - Total active sources: {Source.objects.filter(is_active=True).count()}")

    news_count = Source.objects.filter(is_active=True, source_type='news').count()
    social_count = Source.objects.filter(is_active=True, source_type='social').count()
    print(f"   - News sources: {news_count}")
    print(f"   - Social media sources: {social_count}")

    print("\n" + "=" * 70)
    print("NEWS SOURCES UPDATED SUCCESSFULLY")
    print("=" * 70)

    print("\nActive source categories:")
    print("  • National news: Detik, Kompas, Tempo, CNN Indonesia, Antara")
    print("  • Regional news: Jakarta, Surabaya, Bandung coverage")
    print("  • Crime/Law enforcement: Police and legal news")
    print("  • Business: Industrial area news")
    print("  • English sources: Jakarta Post, Jakarta Globe")
    print("  • Social media: Twitter/X monitoring")

    print("\n⚠️  Note: Configure Twitter API credentials in .env for social media monitoring")

if __name__ == '__main__':
    update_sources()
