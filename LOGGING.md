# Comprehensive Logging for OSINT Dashboard

This document explains the comprehensive logging implemented for the OSINT Dashboard crawler functions.

## Logging Features

### 1. Detailed Progress Tracking
Every step of the scraping process is logged with informative messages:

- **Function Entry**: When a scraping function starts
- **Source Information**: Which source is being processed
- **Keyword Matching**: Number of active keywords for matching
- **Feed Parsing**: RSS feed URL and parsing results
- **Entry Processing**: Each RSS entry processed
- **Article Creation**: When articles are created or skipped
- **Function Exit**: Final results and summary

### 2. Multiple Log Levels

#### INFO Level (General Information)
- Function start/end messages
- Source and keyword counts
- Overall results and summaries

#### DEBUG Level (Detailed Processing)
- Entry-by-entry processing
- Skip reasons for articles
- Intermediate steps

#### WARNING Level (Potential Issues)
- Feed parsing warnings
- Non-critical issues that don't stop processing

#### ERROR Level (Critical Failures)
- Exceptions and errors
- Failed article creations
- Network or parsing errors

### 3. Specific Logging Examples

#### News Source Scraping
```
INFO: Starting scrape_news_source for Reuters (ID: 1)
INFO: Found 32 active keywords for matching
INFO: Parsing RSS feed: https://feeds.bbci.co.uk/news/world/rss.xml
INFO: Feed parsed. Bozo flag: False. Entries found: 28
DEBUG: Skipping entry 1: No keyword matches in title/summary, fetching full article
DEBUG: Entry 1: No keyword matches found
INFO: Successfully scraped Reuters. Created 0 articles, skipped 28.
```

#### Social Media Scraping
```
INFO: Starting scrape_social_media_source for Twitter (ID: 11)
INFO: Found 32 active keywords for Twitter search
INFO: Twitter search query: "terrorism" OR "bomb" OR "explosion" ...
INFO: Initialized Twitter API client
INFO: Twitter search completed. Response data: True
INFO: Processed 5 user profiles from Twitter response
INFO: Created Twitter post: Breaking: Major incident reported...
```

#### Scheduler Operations
```
INFO: Starting run_scheduled_scraping for all active sources
INFO: Found 3 active sources
INFO: Processing source: Reuters (Type: news)
INFO: Queued news scraping for Reuters
INFO: Processing source: Twitter (Type: social)
INFO: Queued social media scraping for Twitter
INFO: Scheduled scraping started for 2 sources
```

### 4. Dashboard Integration

When you click "Run Now" on tasks in the scheduler dashboard:

1. **Task Initiation**: "Manually running crawl task ID: 3"
2. **Source Identification**: "Found task: Hourly News Crawl (Source: Reuters)"
3. **Log Entry Creation**: "Created log entry for task Hourly News Crawl"
4. **Task Queueing**: "Queueing news scraping task for Reuters"
5. **Task Status Update**: "Updated task Hourly News Crawl status to running"
6. **Completion**: "Task Hourly News Crawl started successfully"

### 5. Error Handling and Recovery

#### Network Errors
```
ERROR: Error scraping Reuters: HTTPSConnectionPool(host='feeds.reuters.com', port=443): Max retries exceeded
```

#### Database Errors
```
ERROR: Error creating article 'Breaking News': Database connection failed
```

#### API Errors
```
ERROR: Error scraping Twitter: Invalid bearer token
```

### 6. Performance Monitoring

#### Processing Speed
```
DEBUG: Entry 5: Keyword matches found - {'\\battack(s|ed|ing)?\\b'}
INFO: Created article: Attack on embassy...
DEBUG: Entry 6: No keyword matches found
```

#### Rate Limiting
```
DEBUG: Entry 3: No keyword matches in title/summary, fetching full article
# 0.7 second delay here
```

### 7. Deduplication Logging

```
DEBUG: Skipping entry 2: Article already exists (https://example.com/article)
DEBUG: Skipping entry 7: Article already exists (https://example.com/article2)
```

## Viewing Logs

### During Development
Logs are visible in the terminal when running:
- `python manage.py runserver`
- `celery -A osint_dashboard worker --loglevel=info`
- `celery -A osint_dashboard beat --loglevel=info`

### In Production
Logs should be configured to write to files:
```python
# settings.py
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': '/var/log/osint/dashboard.log',
        },
    },
    'loggers': {
        'scraper.tasks': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
```

## Best Practices for Monitoring

### 1. Real-time Monitoring
Watch for:
- High skip rates (may indicate keyword issues)
- Frequent errors (may indicate source problems)
- Zero article creation (may indicate feed issues)

### 2. Periodic Review
Check logs for:
- Pattern changes in feed formats
- New error types
- Performance degradation

### 3. Alerting
Set up alerts for:
- Critical errors
- Zero article creation for extended periods
- High failure rates

## Example Monitoring Script

```python
import logging
from scraper.tasks import scrape_news_source
from scraper.models import Source

# Enable INFO level logging
logging.basicConfig(level=logging.INFO)

# Test with verbose output
source = Source.objects.filter(name='Reuters').first()
if source:
    result = scrape_news_source(source.id)
    print("Final result:", result)
```

This will show detailed progress information as the scraping occurs.