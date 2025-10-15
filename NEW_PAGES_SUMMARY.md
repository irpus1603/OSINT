# New Pages for Man Guarding Services

## Changes Made

### ✅ Removed/Replaced:
- **Sentiment Analysis** page (less relevant for security operations)

### ✅ Added New Pages:

## 1. Klasifikasi Ancaman (Threat Classification)
**URL**: `/dashboard/threat-classification/`

### Features:
- **6 Threat Categories:**
  1. Pencurian & Perampokan (Theft & Robbery)
  2. Kerusuhan & Demo (Riots & Demonstrations)
  3. Terorisme & Ancaman Bom (Terrorism & Bomb Threats)
  4. Pengrusakan & Vandalisme (Vandalism & Sabotage)
  5. Kejahatan Lainnya (Other Crimes)
  6. Kecelakaan & Darurat (Accidents & Emergencies)

### Display:
- Total threats detected
- Threat count per category
- Severity level (Tinggi/Sedang/Rendah)
- Percentage of total threats
- Progress bars showing distribution
- Recent incidents for each category (top 5)
- Quick regional status overview

### Use Case:
Helps security supervisors understand **what types of threats** are most prevalent in their area of operations.

---

## 2. Status Keamanan Regional (Regional Security Status)
**URL**: `/dashboard/regional-security/`

### Features:
- **6 Monitored Regions:**
  1. **Jakarta** - CBD offices, industrial areas, residential, retail
  2. **Bekasi** - MM2100, EJIP industrial zones
  3. **Cikarang** - Jababeka, Delta Silicon, MM2100
  4. **Tangerang** - BSD, Gading Serpong, Industrial zones
  5. **Surabaya** - SIER, Rungkut Industrial, CBD, Port
  6. **Bandung** - Majalaya Industrial, offices, education

### Each Region Shows:
- **Security Status**: Normal / Waspada / Siaga / Kritis
- **Threat Count**: Total threats detected
- **Threat Breakdown**:
  - Pencurian (Theft)
  - Demo (Demonstrations)
  - Kerusuhan (Riots)
  - Kecelakaan (Accidents)
- **Top Threat Type**: Most common threat
- **Key Areas**: Specific locations monitored
- **Recent Incidents**: Latest 3 incidents

### Status Levels:
- 🟢 **Normal**: < 5 threats
- 🔵 **Waspada**: 5-9 threats
- 🟡 **Siaga**: 10-14 threats
- 🔴 **Kritis**: ≥ 15 threats

### Use Case:
Helps deployment teams understand **where to allocate resources** and which regions need heightened security measures.

---

## Navigation Update

**Old Navigation:**
```
├── Dashboard Utama
├── Analisis Sentimen ❌ (Removed)
├── Laporan Keamanan
├── Kata Kunci Teratas
├── Sumber Berita
├── Peringatan
└── Penjadwalan Crawl
```

**New Navigation:**
```
├── Dashboard Utama
├── Klasifikasi Ancaman ✅ (New)
├── Status Keamanan Regional ✅ (New)
├── Laporan Keamanan
├── Kata Kunci Teratas
├── Sumber Berita
├── Peringatan
└── Penjadwalan Crawl
```

---

## Technical Implementation

### Files Created:
1. `/dashboard/views.py` - Added `threat_classification_view()` and `regional_security_view()`
2. `/templates/dashboard/threat_classification.html` - Threat classification template
3. `/templates/dashboard/regional_security.html` - Regional security template

### Files Modified:
1. `/dashboard/urls.py` - Added new URL routes
2. `/templates/base.html` - Updated navigation menu

### Data Sources:
- Uses existing `Article` model and keywords
- Categorizes based on keyword matching
- Extracts regional information from article content
- Calculates threat levels dynamically

---

## How It Works

### Threat Classification:
1. Fetches articles from last 7 days
2. Matches article keywords to predefined threat categories
3. Counts occurrences per category
4. Calculates percentages and severity
5. Shows recent incidents per category

### Regional Security:
1. Fetches articles from last 7 days
2. Searches for region-specific keywords in article content
3. Categorizes threats by type (pencurian/demo/kerusuhan/etc)
4. Determines security status based on threat count
5. Shows breakdown and recent incidents per region

---

## Benefits for Man Guarding Operations

### Operational Intelligence:
✅ **Know what threats to prepare for** (threat classification)
✅ **Know where threats are occurring** (regional security)
✅ **Adjust patrol routes** based on threat hotspots
✅ **Allocate personnel** to high-risk regions
✅ **Brief security teams** with relevant threat intelligence

### Actionable Insights:
- "Cikarang has 15 threats (Kritis) - mostly demo buruh"
  → Deploy extra personnel to industrial zones

- "Jakarta CBD has rising pencurian incidents"
  → Increase patroli frequency, brief teams on modus operandi

- "Bekasi shows Waspada status with demo activity"
  → Coordinate with local police, prepare crowd control

### Client Reporting:
- Show clients their region's security status
- Demonstrate proactive monitoring
- Justify additional security measures
- Professional, data-driven recommendations

---

## Testing

### To Test:
```bash
# Start server
./start_server.sh

# Visit new pages
http://127.0.0.1:8000/dashboard/threat-classification/
http://127.0.0.1:8000/dashboard/regional-security/
```

### Sample Data:
The views will analyze existing articles in the database. If you need more data:
```bash
# Trigger manual crawl
http://127.0.0.1:8000/scheduler/
# Click "Run Task"
```

---

## Future Enhancements

### Possible Additions:
1. **Interactive Map** - Visual heat map of threats by region
2. **Timeline View** - Chronological incident tracking
3. **Trend Analysis** - Week-over-week comparison
4. **Export to PDF** - Regional security reports
5. **Alert Triggers** - Automatic notifications when status changes to Siaga/Kritis
6. **Facility-Specific Views** - Filter by client locations
7. **Patrol Route Suggestions** - Based on threat hotspots

---

## Summary

**Sentiment Analysis** ❌ → **Threat Classification** ✅ + **Regional Security** ✅

These new pages provide **actionable intelligence** specifically designed for **man guarding operations** in Indonesia, focusing on:
- 🎯 **What** threats are happening (classification)
- 📍 **Where** threats are happening (regional)
- 🛡️ **How to respond** (status-based recommendations)

All in **Bahasa Indonesia** with **security industry terminology**.
