#!/usr/bin/env python
"""
Add new Indonesian news RSS feeds
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'osint_dashboard.settings')
django.setup()

from scraper.models import Source

# New RSS feeds to add
NEW_FEEDS = [
    {
        'name': 'ANTARA News English',
        'url': 'https://en.antaranews.com/rss/news.xml',
        'source_type': 'news'
    },
    {
        'name': 'VIVA.co.id',
        'url': 'https://www.viva.co.id/get/all',
        'source_type': 'news'
    },
    {
        'name': 'SINDOnews',
        'url': 'https://www.sindonews.com/feed',
        'source_type': 'news'
    },
    {
        'name': 'JPNN.com',
        'url': 'https://www.jpnn.com/index.php?mib=rss',
        'source_type': 'news'
    },
    {
        'name': 'Fajar.co.id',
        'url': 'https://fajar.co.id/feed',
        'source_type': 'news'
    },
    {
        'name': 'Waspada Online',
        'url': 'https://waspada.co.id/feed',
        'source_type': 'news'
    },
    {
        'name': 'Online24jam',
        'url': 'https://online24jam.com/feed',
        'source_type': 'news'
    },
]

def add_feeds():
    """Add new feeds to database"""

    print("=" * 70)
    print("ADDING NEW RSS FEEDS")
    print("=" * 70)

    added = 0
    updated = 0
    skipped = 0

    for feed in NEW_FEEDS:
        existing = Source.objects.filter(url=feed['url']).first()

        if existing:
            if not existing.is_active:
                existing.is_active = True
                existing.name = feed['name']
                existing.save()
                print(f"✓ Reactivated: {feed['name']}")
                updated += 1
            else:
                print(f"⊘ Already active: {feed['name']}")
                skipped += 1
        else:
            Source.objects.create(
                name=feed['name'],
                url=feed['url'],
                source_type=feed['source_type'],
                is_active=True
            )
            print(f"+ Added: {feed['name']}")
            print(f"  URL: {feed['url']}")
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
    print("NEXT STEPS")
    print("=" * 70)
    print("1. Trigger crawl: python trigger_crawl_now.py")
    print("2. Monitor: tail -f scraper.log")
    print("3. Dashboard: http://127.0.0.1:8000/dashboard/")

if __name__ == '__main__':
    add_feeds()
