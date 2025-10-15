# Scheduler Guide - OSINT Man Guarding Services

## Overview
The scheduler has been simplified to run **2 active crawl tasks** that automatically monitor Indonesian security news for man guarding operations.

## Active Crawl Tasks

### 1. Crawl Berita Indonesia (Setiap Jam) ⏰ Hourly
- **What it does**: Crawls all 18 Indonesian news sources every hour
- **Sources**: Detik, Kompas, Tempo, CNN Indonesia, Antara, Tribun, Sindonews, Liputan6, VIVA, Republika, etc.
- **Keywords**: 105 security-related keywords (pencurian, perampokan, kerusuhan, demo, satpam, etc.)
- **Purpose**: Get fresh security news updates throughout the day

### 2. Crawl Harian Menyeluruh 📅 Daily
- **What it does**: Comprehensive daily crawl of all news sources
- **When**: Once per day
- **Purpose**: Ensure no security news is missed with a full sweep

### 3. Monitoring Media Sosial (Harian) ⏸️ Disabled
- **Status**: Disabled by default
- **Reason**: Requires Twitter API configuration
- **To enable**: Add `TWITTER_BEARER_TOKEN` to `.env` file

## How the Scheduler Works

### Automatic Execution (Celery Beat)
When you start the services with `./start_server.sh`, Celery Beat automatically runs tasks based on their schedule:
- **Hourly task**: Runs every hour (next run time auto-calculated)
- **Daily task**: Runs once per day (next run time auto-calculated)

### Manual Execution
You can also trigger tasks manually:
1. Go to: http://127.0.0.1:8000/scheduler/
2. Find the task you want to run
3. Click **"Run Task"** button
4. View progress in the logs section

## Quick Start

### 1. Setup (One-time)
```bash
# Update keywords and sources for man guarding
python update_keywords_man_guarding.py
python update_sources_man_guarding.py

# Setup simplified scheduler
python setup_simple_scheduler.py
```

### 2. Start Services
```bash
# Start Redis, Celery Worker, Celery Beat, and Django
./start_server.sh
```

### 3. Access Scheduler Dashboard
Open: http://127.0.0.1:8000/scheduler/

You'll see:
- ✅ Celery status (Worker & Beat running)
- 📋 Active crawl tasks
- 📊 Recent crawl logs
- 🎯 Manual run buttons

## Scheduler Dashboard Features

### Status Indicators
- **🟢 Green**: Celery is running properly
- **🔴 Red**: Celery worker or beat is not running
- **Active/Inactive**: Task enabled/disabled status

### Controls
- **Run Task**: Manually trigger a crawl immediately
- **Enable/Disable**: Toggle task active status
- **View Logs**: See crawl history and results

### Logs Section
Shows recent crawl activity:
- Started time
- Finished time
- Status (Success/Failed)
- Items scraped
- Error messages (if any)

## Managing Tasks

### View Current Tasks
```bash
python manage.py shell -c "from scheduler.models import CrawlTask; [print(f'{t.name}: {t.frequency} - Active: {t.is_active}') for t in CrawlTask.objects.all()]"
```

### Reset Scheduler (if needed)
```bash
python setup_simple_scheduler.py
```
This will:
- Delete old tasks
- Create fresh simplified tasks
- Clean up old logs (keeps last 100)

### Enable/Disable Tasks
Use the scheduler dashboard UI or:
```python
from scheduler.models import CrawlTask

# Disable a task
task = CrawlTask.objects.get(name='Crawl Berita Indonesia (Setiap Jam)')
task.is_active = False
task.save()

# Enable a task
task.is_active = True
task.save()
```

## Troubleshooting

### Celery Not Running
**Problem**: Dashboard shows "Celery worker/beat not running"

**Solution**:
```bash
# Stop all services
./stop_server.sh

# Restart services
./start_server.sh
```

### Tasks Not Executing
**Check 1**: Are tasks active?
- Go to scheduler dashboard
- Verify tasks show "Active: True"

**Check 2**: Is next run time in the future?
- Tasks only run when `next_run` time has passed
- Use "Run Task" button for immediate execution

**Check 3**: Check Celery logs
```bash
# View worker log
tail -f celery_worker.log

# View beat scheduler log
tail -f celery_beat.log
```

### No Articles Being Created
**Check 1**: Are keywords matching?
- View scraper log: `scraper.log`
- Check if news contains your keywords

**Check 2**: Are sources working?
```bash
# Test a specific source
python manage.py shell -c "from scraper.tasks import scrape_news_source; scrape_news_source(1)"
```

**Check 3**: Check source URLs
```bash
# Verify sources are accessible
python manage.py shell -c "from scraper.models import Source; [print(f'{s.name}: {s.url}') for s in Source.objects.filter(is_active=True)]"
```

### Too Many/Too Few Articles
**Adjust keywords**:
```bash
# Edit keywords
nano update_keywords_man_guarding.py

# Re-run to update
python update_keywords_man_guarding.py
```

**Adjust crawl frequency**:
```python
from scheduler.models import CrawlTask

# Change hourly to every 2 hours (modify code)
# or change daily to twice daily
```

## Monitoring & Maintenance

### Check Crawl Statistics
```bash
# View recent articles
python manage.py shell -c "from scraper.models import Article; print(f'Total articles: {Article.objects.count()}'); print(f'Last 24h: {Article.objects.filter(scraped_at__gte=timezone.now() - timedelta(days=1)).count()}')"
```

### View Logs
```bash
# Scraper log
tail -f scraper.log

# Celery worker log
tail -f celery_worker.log

# Celery beat scheduler log
tail -f celery_beat.log
```

### Database Maintenance
```bash
# Clean up old articles (older than 90 days)
python manage.py shell -c "from scraper.models import Article; from django.utils import timezone; from datetime import timedelta; old = Article.objects.filter(published_at__lt=timezone.now() - timedelta(days=90)); print(f'Deleting {old.count()} old articles'); old.delete()"
```

## Configuration Files

- **Scheduler Tasks**: `scheduler/tasks.py`
- **Scraper Tasks**: `scraper/tasks.py`
- **Scheduler Views**: `scheduler/views.py`
- **Models**: `scheduler/models.py`

## API Endpoints

Manual control via API:

```bash
# Run specific task
curl -X POST http://127.0.0.1:8000/scheduler/task/{task_id}/run/

# Run all scheduled tasks
curl -X POST http://127.0.0.1:8000/scheduler/run-scheduled/

# Get Celery status
curl http://127.0.0.1:8000/scheduler/celery-status/

# Stop all tasks
curl -X POST http://127.0.0.1:8000/scheduler/stop-all/

# Start all tasks
curl -X POST http://127.0.0.1:8000/scheduler/start-all/
```

## Best Practices

### For Production
1. **Monitor regularly**: Check scheduler dashboard daily
2. **Review logs**: Look for failed tasks or errors
3. **Adjust frequency**: Based on how much news you need
4. **Backup data**: Regular database backups
5. **Update keywords**: As security landscape changes

### For Development
1. **Start with manual runs**: Test tasks manually first
2. **Check one source**: Before enabling all sources
3. **Monitor resources**: Ensure server can handle load
4. **Use test data**: Before going live

## Summary

**Simple Setup**:
1. Run `./start_server.sh`
2. Visit http://127.0.0.1:8000/scheduler/
3. Click "Run Task" to test manually
4. Let Celery Beat handle automatic scheduling

**Two Tasks**:
- Hourly: Fresh news every hour
- Daily: Comprehensive daily sweep

**Focus**: Indonesian security news for man guarding operations with 105 relevant keywords monitoring 18 news sources.

---

Last updated: 2025-10-07
