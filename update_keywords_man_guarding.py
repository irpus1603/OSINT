#!/usr/bin/env python
"""
Update keywords for man guarding services focus
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'osint_dashboard.settings')
django.setup()

from scraper.models import Keyword

# Man guarding / security services relevant keywords
MAN_GUARDING_KEYWORDS = [
    # Physical security threats (Bahasa Indonesia)
    'pencurian', 'perampokan', 'maling', 'pembobolan', 'pengrusakan',
    'vandalisme', 'sabotase', 'pembakaran', 'kebakaran', 'kebocoran',

    # Criminal activities
    'kriminal', 'kejahatan', 'penodongan', 'pencopetan', 'penjambretan',
    'penculikan', 'terorisme', 'bom', 'ancaman bom', 'benda mencurigakan',

    # Labor and demonstrations
    'demo', 'unjuk rasa', 'demonstrasi', 'mogok kerja', 'buruh',
    'aksi massa', 'kerusuhan', 'ricuh', 'bentrok', 'anarki',

    # Facility security
    'keamanan pabrik', 'keamanan perkantoran', 'keamanan gedung',
    'keamanan perumahan', 'keamanan retail', 'keamanan mall',

    # Security operations
    'satpam', 'security', 'petugas keamanan', 'jaga malam', 'patroli',
    'pos jaga', 'kontrol akses', 'pengawalan', 'evakuasi', 'tanggap darurat',

    # Regional security (major cities)
    'keamanan jakarta', 'keamanan surabaya', 'keamanan bandung',
    'keamanan semarang', 'keamanan medan', 'keamanan bekasi',
    'keamanan tangerang', 'keamanan bogor', 'keamanan cikarang',

    # Industrial areas
    'kawasan industri', 'pabrik', 'gudang', 'pergudangan', 'logistik',

    # Public safety incidents
    'kecelakaan kerja', 'kebocoran gas', 'bahaya kimia', 'darurat medis',
    'orang hilang', 'orang mencurigakan', 'pengunjung mencurigakan',

    # Law enforcement coordination
    'polisi', 'polsek', 'polres', 'polda', 'aparat', 'TNI',
    'laporan polisi', 'koordinasi keamanan',

    # Surveillance and monitoring
    'CCTV', 'kamera pengawas', 'sistem keamanan', 'alarm', 'sensor',
    'deteksi dini', 'monitoring', 'pengawasan',

    # English equivalents (for international news)
    'theft', 'robbery', 'burglary', 'vandalism', 'sabotage',
    'security breach', 'trespassing', 'unauthorized access',
    'riot', 'protest', 'strike', 'terrorism', 'bomb threat',

    # Threat levels and alerts
    'ancaman', 'bahaya', 'siaga', 'waspada', 'awas', 'hati-hati',
    'peringatan dini', 'status siaga', 'keadaan darurat',
]

def update_keywords():
    """Update keywords in database"""

    print("=" * 60)
    print("UPDATING KEYWORDS FOR MAN GUARDING SERVICES")
    print("=" * 60)

    # Deactivate old keywords first
    print("\n1. Deactivating old keywords...")
    old_count = Keyword.objects.filter(is_active=True).update(is_active=False)
    print(f"   Deactivated {old_count} old keywords")

    # Add new man guarding keywords
    print("\n2. Adding man guarding keywords...")
    created_count = 0
    updated_count = 0

    for term in MAN_GUARDING_KEYWORDS:
        keyword, created = Keyword.objects.get_or_create(
            term=term.lower(),
            defaults={'is_active': True}
        )

        if created:
            created_count += 1
            print(f"   ✓ Created: {term}")
        else:
            if not keyword.is_active:
                keyword.is_active = True
                keyword.save()
                updated_count += 1
                print(f"   ✓ Reactivated: {term}")

    print(f"\n3. Summary:")
    print(f"   - New keywords created: {created_count}")
    print(f"   - Keywords reactivated: {updated_count}")
    print(f"   - Total active keywords: {Keyword.objects.filter(is_active=True).count()}")

    print("\n" + "=" * 60)
    print("KEYWORDS UPDATED SUCCESSFULLY")
    print("=" * 60)

    print("\nActive keyword categories:")
    print("  • Physical security threats (pencurian, perampokan, vandalisme)")
    print("  • Criminal activities (kriminal, terorisme, penculikan)")
    print("  • Labor issues (demo, mogok kerja, buruh)")
    print("  • Facility security (keamanan pabrik, gedung, perumahan)")
    print("  • Security operations (satpam, patroli, pos jaga)")
    print("  • Regional monitoring (Jakarta, Surabaya, Bandung, etc)")
    print("  • Industrial areas (kawasan industri, pabrik, gudang)")
    print("  • Emergency response (evakuasi, tanggap darurat)")
    print("  • Law enforcement (polisi, aparat, koordinasi)")
    print("  • Surveillance (CCTV, monitoring, alarm)")

if __name__ == '__main__':
    update_keywords()
