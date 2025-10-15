# Man Guarding Services OSINT Configuration

## Overview
The OSINT Dashboard has been configured specifically for **man guarding services (jasa pengamanan/satpam)** to monitor security threats and provide actionable intelligence for physical security operations in Indonesia.

## Configuration Changes

### 1. LLM Analysis Prompts (✓ Updated)

**File**: `dashboard/llm_client.py`

All analysis prompts have been updated to:
- Generate reports in **Bahasa Indonesia**
- Use **man guarding industry terminology**: satpam, pos jaga, patroli, pengawalan, kontrol akses, CCTV, koordinasi dengan aparat, eskalasi insiden
- Focus on **operational security concerns**: physical threats, facility protection, criminal activities, labor demonstrations
- Provide **actionable recommendations** for security personnel

#### Analysis Types:
1. **Security Summary** (`generate_security_summary`)
   - Focus on physical security threats (pencurian, perampokan, pengrusakan, terorisme)
   - Crime trends relevant to client locations (offices, factories, residential, retail)
   - Regional security conditions (Jakarta, Surabaya, Bandung, etc.)
   - Labor issues (demos, strikes, riots)
   - Operational recommendations for guard posts and patrols

2. **Trend Analysis** (`generate_trend_analysis`)
   - Escalating security concerns
   - Threat landscape changes
   - Recommendations for patrol procedures and surveillance

3. **Incident Analysis** (`generate_incident_analysis`)
   - Incident categorization (theft, riots, terrorism, etc.)
   - Severity assessment
   - SOP recommendations for guard posts and patrols
   - Preventive measures
   - Escalation protocols and coordination with law enforcement
   - Personnel training needs
   - Equipment requirements

### 2. Keywords (✓ Updated - 105 Active Keywords)

**Script**: `update_keywords_man_guarding.py`

Keywords now focus on man guarding operations:

#### Categories:
- **Physical Security Threats**: pencurian, perampokan, maling, pembobolan, pengrusakan, vandalisme, sabotase, pembakaran
- **Criminal Activities**: kriminal, kejahatan, penodongan, pencopetan, penjambretan, penculikan, terorisme, bom, ancaman bom
- **Labor & Demonstrations**: demo, unjuk rasa, demonstrasi, mogok kerja, buruh, aksi massa, kerusuhan, ricuh, bentrok
- **Facility Security**: keamanan pabrik, keamanan perkantoran, keamanan gedung, keamanan perumahan, keamanan retail, keamanan mall
- **Security Operations**: satpam, security, petugas keamanan, jaga malam, patroli, pos jaga, kontrol akses, pengawalan, evakuasi, tanggap darurat
- **Regional Monitoring**: keamanan jakarta, keamanan surabaya, keamanan bandung, keamanan semarang, keamanan medan, keamanan bekasi, keamanan tangerang, keamanan bogor, keamanan cikarang
- **Industrial Areas**: kawasan industri, pabrik, gudang, pergudangan, logistik
- **Emergency Response**: kecelakaan kerja, kebocoran gas, bahaya kimia, darurat medis, orang hilang, orang mencurigakan
- **Law Enforcement**: polisi, polsek, polres, polda, aparat, TNI, laporan polisi, koordinasi keamanan
- **Surveillance**: CCTV, kamera pengawas, sistem keamanan, alarm, sensor, deteksi dini, monitoring, pengawasan
- **Threat Levels**: ancaman, bahaya, siaga, waspada, awas, hati-hati, peringatan dini, status siaga, keadaan darurat

#### Update Command:
```bash
python update_keywords_man_guarding.py
```

### 3. News Sources (✓ Updated - 19 Active Sources)

**Script**: `update_sources_man_guarding.py`

Sources now focus on Indonesian security news:

#### National News Sources:
- Detik News
- Kompas
- Tempo (Metro section)
- CNN Indonesia - Nasional
- Antara News
- Tribun News
- Sindonews
- Liputan6
- VIVA News
- Republika

#### Regional News Sources:
- **Jakarta**: Jakarta Tribune, Berita Jakarta
- **Surabaya**: Surya Surabaya
- **West Java**: Tribun Jabar

#### Specialized Sources:
- **Crime/Law Enforcement**: Kompas - Hukum Kriminal
- **Business/Industrial**: Bisnis Indonesia
- **English Coverage**: The Jakarta Post, Jakarta Globe

#### Social Media:
- Twitter/X Indonesia (requires API credentials in .env)

#### Update Command:
```bash
python update_sources_man_guarding.py
```

## Target Audience

The system now serves:
- **Man guarding companies** (perusahaan jasa pengamanan)
- **Security supervisors** (supervisor satpam)
- **Operations managers** managing guard deployments
- **Risk assessment teams** for client sites
- **Security coordinators** liaising with law enforcement

## Use Cases

### 1. Pre-Deployment Intelligence
Monitor security conditions in areas where clients are located:
- Industrial zones (Cikarang, Bekasi, Karawang)
- Commercial districts (Jakarta CBD, Surabaya)
- Residential areas

### 2. Threat Monitoring
Track emerging threats relevant to guarded facilities:
- Theft and burglary trends
- Labor demonstrations near client sites
- Civil unrest and riots
- Terrorism threats
- Criminal activities in vicinity

### 3. Operational Planning
Adjust security measures based on intelligence:
- Increase patrol frequency during high-risk periods
- Deploy additional personnel for demonstrations
- Implement enhanced access control measures
- Coordinate with local police

### 4. Client Reporting
Generate professional security reports in Bahasa Indonesia:
- Weekly threat briefings
- Incident analysis
- Security recommendations
- Regional risk assessments

## Report Terminology

All reports use Indonesian man guarding industry terms:

### Security Operations:
- **Satpam/Security**: Security guard
- **Pos jaga**: Guard post/checkpoint
- **Patroli**: Patrol
- **Pengawalan**: Escort/convoy security
- **Kontrol akses**: Access control
- **Jaga malam**: Night shift guard
- **Petugas keamanan**: Security officer

### Incidents:
- **Pencurian**: Theft
- **Perampokan**: Robbery
- **Pengrusakan**: Vandalism/destruction
- **Penyusupan**: Intrusion/trespassing
- **Kerusuhan**: Riot/civil unrest
- **Ancaman bom**: Bomb threat

### Response:
- **Tanggap darurat**: Emergency response
- **Evakuasi**: Evacuation
- **Eskalasi insiden**: Incident escalation
- **Koordinasi dengan aparat**: Coordination with law enforcement
- **Laporan polisi**: Police report

### Risk Levels:
- **Rendah**: Low
- **Sedang**: Medium
- **Tinggi**: High
- **Kritis**: Critical

## Next Steps

1. **Configure Twitter API** (optional):
   Add to `.env`:
   ```
   TWITTER_BEARER_TOKEN=your_token_here
   ```

2. **Run Initial Crawl**:
   ```bash
   python manage.py scrape_sources
   ```

3. **Initialize Scheduled Tasks**:
   ```bash
   python manage.py init_crawl_tasks
   ```

4. **Start Services**:
   ```bash
   ./start_server.sh
   ```

5. **Access Dashboard**:
   - Main Dashboard: http://127.0.0.1:8000/dashboard/
   - View LLM-generated security analysis
   - Export reports in Bahasa Indonesia

## Files Modified

1. `/dashboard/llm_client.py` - LLM prompts for Bahasa Indonesia analysis
2. `/update_keywords_man_guarding.py` - Keyword update script (new)
3. `/update_sources_man_guarding.py` - News source update script (new)
4. Database: Keywords and Sources tables updated

## Support

For questions or adjustments:
- Keywords: Edit `update_keywords_man_guarding.py` and re-run
- News sources: Edit `update_sources_man_guarding.py` and re-run
- LLM prompts: Edit `dashboard/llm_client.py`
- Add more cities: Update keywords and sources scripts

---

**Status**: ✓ Fully Configured for Man Guarding Services Operations
**Language**: Bahasa Indonesia
**Region Focus**: Indonesia (Jakarta, Surabaya, Bandung, major cities)
**Industry**: Jasa Pengamanan / Physical Security Services
