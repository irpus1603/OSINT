# OSINT Dashboard Scraper

The OSINT Dashboard includes a comprehensive scraping system for collecting security-related content from news media and social media sources.

## Architecture

The scraper system consists of several components:

1. **Data Models** - Django models for storing sources, keywords, articles, and posts
2. **Scraping Tasks** - Celery tasks for performing the actual scraping
3. **Scheduler** - Django app for managing scheduled scraping tasks
4. **Services** - Business logic layer for coordinating scraping operations
5. **Management Commands** - CLI tools for manual scraping operations

## Data Models

### Source
Represents a data source (news RSS feed or social media platform)

### Keyword
Security-related terms used for filtering content

### Article
News articles collected from RSS feeds

### Post
Social media posts collected from platforms like Twitter

## Scraping Implementation

### News Media Scraping
- Uses `feedparser` to parse RSS feeds
- Applies keyword matching to identify security-related content
- Optionally fetches full article text for deeper matching
- Stores results in the Article model

### Social Media Scraping
- Uses `tweepy` to access Twitter API v2
- Searches for keywords in recent tweets
- Stores results in the Post model

## Running Scraping Tasks

### Manual Scraping
```bash
# Scrape all active sources
python manage.py scrape_sources

# Scrape a specific source by ID
python manage.py scrape_sources --source-id 1

# Show scraping statistics
python manage.py scrape_sources --stats
```

### Scheduled Scraping
The scheduler app manages recurring scraping tasks:
- Hourly, daily, or weekly frequency
- Automatic execution via Celery beat
- Task status tracking and logging

### Celery Tasks
```bash
# Start Celery worker
celery -A osint_dashboard worker -l info

# Start Celery beat (scheduler)
celery -A osint_dashboard beat -l info
```

## Configuration

### Environment Variables
```env
TWITTER_BEARER_TOKEN=your-twitter-api-token
REDIS_URL=redis://localhost:6379/0
```

### Supported Sources
- Reuters
- BBC World
- CNN International
- Al Jazeera
- AP News
- Kompas
- Detikcom
- CNN Indonesia
- Antara News
- The Jakarta Post
- Twitter

## Keyword Matching

The system uses regex patterns to match security-related keywords in both English and Indonesian:

### English Keywords
- terrorism, bomb, explosion, attack, militant, insurgent
- hostage, shooting, threat, security, riot, protest
- demonstration, extremist, radicalization, cyber attack

### Indonesian Keywords
- terorisme, bom, ledakan, serangan, milisi, pemberontak
- sandera, penembakan, ancaman, keamanan, kerusuhan, demo
- unjuk rasa, penculikan, ekstremis, radikalisasi

## Data Processing

1. **Content Collection** - Fetch content from sources
2. **Keyword Matching** - Apply regex patterns to identify relevant content
3. **Data Storage** - Save matched content to database
4. **Deduplication** - Prevent duplicate entries
5. **Metadata Extraction** - Extract publication dates, authors, etc.