#!/usr/bin/env python
"""
Additional reliable Indonesian news feeds for man guarding services
Focus: Security, crime, regional news, labor issues
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'osint_dashboard.settings')
django.setup()

from scraper.models import Source

# Additional news feeds (tested and reliable)
ADDITIONAL_FEEDS = [
    # National News - Crime & Security Focus
    {
        'name': 'Okezone News',
        'url': 'https://sindikasi.okezone.com/index.php/rss/1/RSS2.0',
        'source_type': 'news',
        'description': 'Major news portal with strong crime coverage'
    },
    {
        'name': 'Merdeka.com',
        'url': 'https://www.merdeka.com/feed/',
        'source_type': 'news',
        'description': 'National news with crime and regional coverage'
    },
    {
        'name': 'Suara.com',
        'url': 'https://www.suara.com/rss',
        'source_type': 'news',
        'description': 'News portal with crime and local news'
    },

    # Regional - Jakarta
    {
        'name': 'Kompas Jakarta',
        'url': 'https://megapolitan.kompas.com/rss',
        'source_type': 'news',
        'description': 'Jakarta metropolitan news from Kompas'
    },
    {
        'name': 'Detik Megapolitan',
        'url': 'https://rss.detik.com/index.php/megapolitan',
        'source_type': 'news',
        'description': 'Jakarta and cities news from Detik'
    },

    # Regional - East Java
    {
        'name': 'Kompas Jatim',
        'url': 'https://regional.kompas.com/jatim/rss',
        'source_type': 'news',
        'description': 'East Java (Surabaya) regional news'
    },
    {
        'name': 'Tribun Jatim',
        'url': 'https://jatim.tribunnews.com/rss',
        'source_type': 'news',
        'description': 'East Java regional coverage'
    },

    # Regional - West Java
    {
        'name': 'Pikiran Rakyat',
        'url': 'https://www.pikiran-rakyat.com/rss',
        'source_type': 'news',
        'description': 'West Java (Bandung) regional news'
    },
    {
        'name': 'Kompas Jabar',
        'url': 'https://regional.kompas.com/jabar/rss',
        'source_type': 'news',
        'description': 'West Java regional news from Kompas'
    },

    # Law & Crime Specific
    {
        'name': 'Hukumonline',
        'url': 'https://www.hukumonline.com/rss/news',
        'source_type': 'news',
        'description': 'Legal and crime news'
    },

    # Economic/Labor (for demo & strike news)
    {
        'name': 'Bisnis.com',
        'url': 'https://ekonomi.bisnis.com/index.xml',
        'source_type': 'news',
        'description': 'Business news (labor issues, strikes)'
    },
    {
        'name': 'Kontan',
        'url': 'https://nasional.kontan.co.id/rss',
        'source_type': 'news',
        'description': 'Business news with labor coverage'
    },

    # Traffic & Transport (accidents, incidents)
    {
        'name': 'TMC Polda Metro',
        'url': 'https://tmc.id/feed',
        'source_type': 'news',
        'description': 'Traffic and incident reports Jakarta'
    },
]

def add_feeds():
    """Add additional news feeds to database"""

    print("=" * 70)
    print("ADDING ADDITIONAL NEWS FEEDS")
    print("=" * 70)

    added = 0
    skipped = 0
    updated = 0

    for feed in ADDITIONAL_FEEDS:
        # Check if already exists
        existing = Source.objects.filter(url=feed['url']).first()

        if existing:
            if not existing.is_active:
                existing.is_active = True
                existing.name = feed['name']
                existing.save()
                print(f"✓ Reactivated: {feed['name']}")
                updated += 1
            else:
                print(f"⊘ Already exists: {feed['name']}")
                skipped += 1
        else:
            # Create new source
            Source.objects.create(
                name=feed['name'],
                url=feed['url'],
                source_type=feed['source_type'],
                is_active=True
            )
            print(f"+ Added: {feed['name']}")
            print(f"  URL: {feed['url']}")
            print(f"  Description: {feed['description']}")
            print()
            added += 1

    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"✓ New feeds added: {added}")
    print(f"✓ Feeds reactivated: {updated}")
    print(f"⊘ Already active: {skipped}")

    total_active = Source.objects.filter(is_active=True, source_type='news').count()
    print(f"\nTotal active news sources: {total_active}")

    print("\n" + "=" * 70)
    print("RECOMMENDED FEEDS BY CATEGORY")
    print("=" * 70)

    print("\n📰 National News (Crime & Security):")
    print("  • Okezone News - Major portal, strong crime coverage")
    print("  • Merdeka.com - National with regional focus")
    print("  • Suara.com - Local crime and incidents")

    print("\n🏙️ Jakarta/Megapolitan:")
    print("  • Kompas Jakarta (Megapolitan)")
    print("  • Detik Megapolitan")

    print("\n🏭 Regional - Industrial Areas:")
    print("  • Kompas Jatim (Surabaya/East Java)")
    print("  • Kompas Jabar (Bandung/West Java)")
    print("  • Pikiran Rakyat (Bandung focus)")

    print("\n⚖️ Law & Crime:")
    print("  • Hukumonline - Legal and crime news")

    print("\n👷 Labor & Strikes:")
    print("  • Bisnis.com - Business/labor issues")
    print("  • Kontan - Economic with labor coverage")

    print("\n🚗 Traffic & Incidents:")
    print("  • TMC Polda Metro - Real-time incidents Jakarta")

    print("\n" + "=" * 70)
    print("NEXT STEPS")
    print("=" * 70)
    print("\n1. Test feeds:")
    print("   python test_new_feeds.py")
    print("\n2. Trigger immediate crawl:")
    print("   python trigger_crawl_now.py")
    print("\n3. Monitor results:")
    print("   tail -f scraper.log")
    print("\n4. Check dashboard:")
    print("   http://127.0.0.1:8000/dashboard/")

if __name__ == '__main__':
    add_feeds()
