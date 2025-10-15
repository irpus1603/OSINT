"""
LLM API Client for Security Analysis
"""
import requests
import json
import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

class SecurityLLMClient:
    """Client for interacting with LLM API for security analysis"""
    
    def __init__(self, api_url: str = "http://103.67.43.158:9000/v1/chat/completions"):
        self.api_url = api_url
        self.model = "GoToCompany/gemma2-9b-cpt-sahabatai-v1-instruct"
        self.max_tokens = 1024
        self.timeout = 600  # 10 minutes timeout for security report generation

    def _clean_response(self, content: str) -> str:
        """
        Clean LLM response by removing echoed prompts
        Some LLM models echo the user/system prompt in the response
        """
        if not content:
            return content

        # Split content by lines
        lines = content.split('\n')

        # Find where the actual assistant response starts
        # Look for the first line that starts with ## (markdown header) which indicates actual response
        start_index = 0
        for i, line in enumerate(lines):
            stripped = line.strip()
            # The actual response typically starts with a markdown header
            if stripped.startswith('##') and not stripped.startswith('###'):
                start_index = i
                break

        # If we found a response start, return from there
        if start_index > 0:
            return '\n'.join(lines[start_index:]).strip()

        # Otherwise, try to detect and remove "user" role echo
        # LLM sometimes returns: "user\n\n<prompt text>\n\nassistant\n\n<actual response>"
        content_lower = content.lower()

        # Look for common separators
        if '\nassistant\n' in content_lower:
            # Split by assistant marker and take everything after
            parts = content.split('\nassistant\n', 1)
            if len(parts) > 1:
                return parts[1].strip()

        # If no cleaning needed, return as-is
        return content.strip()

    def _make_request(self, messages: List[Dict[str, str]], max_tokens: Optional[int] = None) -> Optional[str]:
        """Make request to LLM API"""
        try:
            payload = {
                "model": self.model,
                "messages": messages,
                "max_tokens": max_tokens or self.max_tokens
            }
            
            headers = {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer WkjYBaVUnoK8SCsWTtUVYBAqer20YiD6nLMiWRY_1Wo'
            }
            
            logger.info(f"Making LLM API request to {self.api_url}")
            response = requests.post(
                self.api_url,
                headers=headers,
                json=payload,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                if 'choices' in result and len(result['choices']) > 0:
                    content = result['choices'][0]['message']['content']
                    logger.info("LLM API request successful")

                    # Clean up response - remove any echoed prompts
                    # Sometimes LLM echoes the user prompt, we want to remove that
                    content = self._clean_response(content)

                    return content
                else:
                    logger.error(f"Unexpected API response format: {result}")
                    return None
            else:
                logger.error(f"API request failed with status {response.status_code}: {response.text}")
                return None
                
        except requests.exceptions.Timeout:
            logger.error("LLM API request timed out")
            return None
        except requests.exceptions.ConnectionError:
            logger.error("Failed to connect to LLM API")
            return None
        except Exception as e:
            logger.error(f"Error making LLM API request: {str(e)}")
            return None
    
    def generate_security_summary(self, articles_data: List[Dict], posts_data: List[Dict],
                                 keywords_data: List[Dict], date_range: str) -> Optional[str]:
        """Generate comprehensive security summary from crawled data for man guarding services"""

        # Prepare data summary for LLM
        articles_summary = []
        for article in articles_data[:10]:  # Limit to top 10 articles
            articles_summary.append({
                'title': article.get('title', '')[:100],
                'source': article.get('source', ''),
                'keywords': [kw.get('term', '') for kw in article.get('keywords', [])][:3],
                'sentiment': article.get('sentiment', 'neutral')
            })

        posts_summary = []
        for post in posts_data[:5]:  # Limit to top 5 posts
            posts_summary.append({
                'content': post.get('content', '')[:150],
                'source': post.get('source', ''),
                'engagement': {
                    'likes': post.get('likes_count', 0),
                    'retweets': post.get('retweets_count', 0)
                }
            })

        top_keywords = [kw.get('keyword', '') for kw in keywords_data[:10]]

        # Create professional OSINT Security & Safety Snapshot based on template
        system_prompt = """Anda adalah analis OSINT keamanan profesional untuk industri jasa pengamanan di Indonesia.

Buat laporan "Daily OSINT Security & Safety Snapshot" dalam Bahasa Indonesia berdasarkan berita yang dikumpulkan dari database. Gunakan format profesional seperti intelligence report.

PENTING:
- Tulis laporan final yang siap dibaca, BUKAN instruksi atau placeholder
- Gunakan data konkret dari berita yang diberikan
- Berikan confidence level untuk setiap temuan
- Fokus pada actionable intelligence untuk operasional security"""

        user_prompt = f"""Buat Daily OSINT Security & Safety Snapshot berdasarkan berita periode {date_range}:

**BERITA YANG DIKUMPULKAN:**
{json.dumps(articles_summary, indent=2)}

**KATA KUNCI TERDETEKSI:**
{', '.join(top_keywords)}

---

## LAPORAN KEAMANAN HARIAN — OSINT Security & Safety Snapshot

**Periode:** {date_range}
**Analyst:** Sahabat-AI OSINT System
**Confidence Note:** Berdasarkan berita publik dan media sosial yang dikumpulkan; mungkin tidak mencakup insiden yang belum dilaporkan.

### 1. KEY INCIDENT ALERTS

Buat tabel insiden kunci dari berita (format markdown table):

| Insiden/Kejadian | Waktu Dilaporkan | Lokasi/Area | Deskripsi & Implikasi | Confidence |
|------------------|------------------|-------------|----------------------|------------|
| [dari berita] | [waktu] | [lokasi] | [detail singkat + implikasi untuk keamanan] | [Low/Medium/High] |

(Ambil 3-5 insiden paling relevan dari berita)

### 2. SUMMARY RISK ASSESSMENT

**Main Risk:** [Identifikasi ancaman utama berdasarkan pola berita - pencurian/perampokan/kerusuhan/dll]

**Secondary Risk:** [Ancaman sekunder - kemacetan/demo/kecelakaan/dll]

**Time-of-Day Focus:** [Waktu berisiko tinggi berdasarkan pola insiden]

**Confidence Level:** [Low/Medium/High] — [jelaskan mengapa: banyak sumber, ada konfirmasi resmi, dll]

**Data Gaps/Caveats:** [Keterbatasan data: belum dikonfirmasi aparat, kemungkinan under-reporting, dll]

### 3. ACTIONABLE RECOMMENDATIONS FOR TODAY

Berikan 5-7 rekomendasi spesifik dan actionable:

- **Patroli & Deployment:** [area spesifik yang perlu penguatan, jam berapa]
- **Hotspot Focus:** [lokasi spesifik dari berita yang perlu perhatian ekstra]
- **Event Response:** [persiapan untuk demo/acara jika ada dari berita]
- **Public Awareness:** [pesan untuk klien/personel tentang ancaman hari ini]
- **CCTV & Monitoring:** [penyesuaian monitoring berdasarkan jam dan area berisiko]
- **Koordinasi:** [koordinasi dengan aparat jika diperlukan]
- **Social Media Monitoring:** [pantau update selama hari berjalan]

### 4. THREAT IMPACT BY SECTOR

**Perkantoran:** [Tingkat risiko: Rendah/Sedang/Tinggi - penjelasan singkat]
**Pabrik/Industri:** [Tingkat risiko - penjelasan singkat]
**Retail/Mall:** [Tingkat risiko - penjelasan singkat]
**Perumahan/Apartemen:** [Tingkat risiko - penjelasan singkat]

---

JANGAN tulis "[dari berita]" atau placeholder. ISI dengan data AKTUAL dari berita yang diberikan."""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        return self._make_request(messages, max_tokens=2048)
    
    def generate_trend_analysis(self, keywords_trends: List[Dict]) -> Optional[str]:
        """Generate professional trend analysis following OSINT template style"""

        system_prompt = """Anda adalah analis tren OSINT keamanan profesional untuk industri jasa pengamanan di Indonesia.

Buat analisis tren keamanan dalam format intelligence report yang profesional. Fokus pada pola, perubahan, dan implikasi operasional.

PENTING: Tulis laporan final, bukan instruksi. Gunakan data konkret."""

        trends_data = []
        for trend in keywords_trends[:10]:
            trends_data.append({
                'keyword': trend.get('keyword', ''),
                'mentions': trend.get('total_mentions', 0),
                'trend_direction': trend.get('trend_direction', 'stable'),
                'trend_percentage': trend.get('trend_percentage', 0),
                'dominant_sentiment': trend.get('dominant_sentiment', 'neutral')
            })

        user_prompt = f"""Buat Security Trend Analysis berdasarkan data tren berikut:

**DATA TREN KEYWORD:**
{json.dumps(trends_data, indent=2)}

---

## ANALISIS TREN KEAMANAN

### TREND SNAPSHOT

**Trending Keywords:** [List top 3-5 keywords dengan arah tren]

**Overall Security Trend:** [Membaik/Stabil/Memburuk/Memburuk Signifikan]

**Confidence Level:** [Low/Medium/High] — [alasan: jumlah data, konsistensi pola, dll]

### PATTERN ANALYSIS

Buat tabel tren utama:

| Keyword | Mentions | Trend Direction | Change % | Category | Implications |
|---------|----------|-----------------|----------|----------|--------------|
| [keyword] | [angka] | [↑/↓/→] | [%] | [jenis ancaman] | [dampak singkat] |

### KEY FINDINGS

**Increasing Threats:** [Keyword/kategori yang meningkat - jelaskan apa artinya untuk operasional]

**Decreasing Trends:** [Keyword/kategori yang menurun - jelaskan konteks]

**Stable Patterns:** [Keyword/kategori yang stabil - baseline risk]

**Geographic Focus:** [Area yang terindikasi dari pola tren]

**Temporal Patterns:** [Pola waktu jika teridentifikasi]

### THREAT DRIVERS & ROOT CAUSES

**Economic Factors:** [Jika relevan: PHK, inflasi, dll]

**Political/Social Factors:** [Jika relevan: pemilu, demo, konflik sosial]

**Seasonal/Event-driven:** [Jika relevan: musim, event khusus]

### OPERATIONAL IMPACT ASSESSMENT

**High Priority Sectors:** [Sektor yang paling terpengaruh tren]

**Emerging Vulnerabilities:** [Celah keamanan baru yang teridentifikasi]

**Resource Allocation Needs:** [Area yang perlu penguatan berdasarkan tren]

### ACTIONABLE RECOMMENDATIONS

**Immediate (1 minggu):**
- [2-3 aksi taktis spesifik berdasarkan tren]

**Short-term (2-4 minggu):**
- [2-3 penyesuaian prosedural]

**Strategic (Jangka panjang):**
- [2-3 inisiatif strategis]

---

ISI dengan analisis AKTUAL dari data tren. JANGAN gunakan placeholder."""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        return self._make_request(messages, max_tokens=1536)
    
    def generate_incident_analysis(self, incident_articles: List[Dict]) -> Optional[str]:
        """Generate professional incident AAR following OSINT template style"""

        system_prompt = """Anda adalah analis insiden OSINT keamanan profesional untuk industri jasa pengamanan di Indonesia.

Buat After-Action Review (AAR) dalam format intelligence report profesional. Fokus pada reconstruction, lessons learned, dan preventive measures.

PENTING: Tulis laporan final, bukan instruksi. Gunakan data aktual dari berita."""

        incidents = []
        for article in incident_articles[:5]:
            incidents.append({
                'title': article.get('title', '')[:120],
                'source': article.get('source', ''),
                'keywords': [kw.get('term', '') for kw in article.get('keywords', [])][:3],
                'excerpt': article.get('excerpt', '')[:200]
            })

        user_prompt = f"""Buat Incident Analysis & After-Action Review berdasarkan berita insiden:

**BERITA INSIDEN:**
{json.dumps(incidents, indent=2)}

---

## INCIDENT AFTER-ACTION REVIEW (AAR)

### INCIDENT SUMMARY TABLE

| Insiden | Waktu Dilaporkan | Lokasi | Kategori | Severity | Korban/Dampak | Confidence |
|---------|------------------|--------|----------|----------|---------------|------------|
| [dari berita] | [waktu] | [lokasi] | [jenis] | [Rendah/Sedang/Tinggi/Kritis] | [detail] | [Low/Med/High] |

### INCIDENT RECONSTRUCTION

**What Happened:**
[1-2 paragraf: kronologi insiden berdasarkan berita, tahapan kejadian (approach, breach, execution, escape)]

**Who Involved:**
- **Threat Actor Profile:** [Kriminal profesional/opportunistic/demonstran/insider/organized crime]
- **Target/Victims:** [Aset/orang yang menjadi target dan korban]
- **Responders:** [Pihak yang merespons: security, polisi, dll]

**When & Timeline:**
- **Time of Incident:** [Waktu kejadian]
- **Duration:** [Berapa lama insiden berlangsung]
- **Response Time:** [Waktu respons jika disebutkan]

**Where:**
- **Location:** [Lokasi spesifik: kota, area, building]
- **Entry/Exit Points:** [Titik masuk dan keluar pelaku jika teridentifikasi]
- **Geographic Pattern:** [Pola lokasi jika ada]

**Why (Motive):**
[Analisis motif: ekonomi (target of opportunity/planned theft), politik (ideological), sosial (grievance), dll]

**How (Modus Operandi):**
[Detail cara pelaku beroperasi, teknik yang digunakan, metode bypass security]

### VULNERABILITY ASSESSMENT

**Exploited Weaknesses:**
- [Celah keamanan yang dieksploitasi dari analisis berita]
- [Procedural gaps atau human error]

**Preventability Assessment:** [Preventable/Partially Preventable/Force Majeure] — [penjelasan]

### RISK ASSESSMENT

**Similar Incident Probability:** [Low/Medium/High] — [Kemungkinan insiden serupa terjadi]

**High-Risk Locations:** [Area dengan vulnerability profile serupa]

**Repeat Attack Potential:** [Assessment kemungkinan pelaku mengulangi aksi]

### CORRECTIVE & PREVENTIVE MEASURES

**Immediate Actions (24-72 jam):**
- [2-3 tindakan kritis untuk menutup gap yang tereksploitasi]

**Short-term Improvements (1-2 minggu):**
- **SOP Pos Jaga:** [Revisi spesifik]
- **Patroli:** [Adjustment rute/frequency]
- **Access Control:** [Strengthening procedures]
- **Surveillance:** [CCTV optimization]
- **Response Protocol:** [Incident response improvements]
- **Personnel Training:** [Security awareness/threat briefing]

**Strategic Initiatives (Jangka Panjang):**
- **Coordination:** [Collaboration dengan aparat]
- **Technology:** [Security tech upgrades]
- **Intelligence Sharing:** [Information exchange programs]

### LESSONS LEARNED

**Key Takeaways:**
[2-3 pelajaran utama yang applicable untuk mencegah insiden serupa]

**Actionable Insights:**
[Specific insights untuk operational security improvement]

---

ISI dengan data AKTUAL dari berita. JANGAN gunakan placeholder."""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        return self._make_request(messages, max_tokens=1536)