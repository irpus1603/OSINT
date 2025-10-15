# Quick Start Guide - OSINT Man Guarding Services

## 🚀 Starting the Application

### 1. Start All Services (One Command)
```bash
./start_server.sh
```
This automatically starts:
- ✓ Redis (if not running)
- ✓ Celery Worker (background tasks)
- ✓ Celery Beat (task scheduler)
- ✓ Django Web Server

### 2. Stop All Services
```bash
./stop_server.sh
```

## 🌐 Access Points

| Service | URL | Purpose |
|---------|-----|---------|
| **Main Dashboard** | http://127.0.0.1:8000/dashboard/ | View security analysis & reports |
| **Scheduler** | http://127.0.0.1:8000/scheduler/ | Manage crawling tasks |
| **Admin Panel** | http://127.0.0.1:8000/admin/ | Database management |
| **API** | http://127.0.0.1:8000/api/ | REST API endpoints |

## 📋 Active Features

### Crawling (Automatic)
- **Hourly**: Crawls 18 Indonesian news sources every hour
- **Daily**: Comprehensive daily sweep
- **Sources**: Detik, Kompas, Tempo, CNN Indonesia, Antara, Tribun, etc.

### Keywords (105 Active)
Security terms for man guarding:
- Physical threats: pencurian, perampokan, vandalisme
- Criminal activity: kriminal, terorisme, penculikan
- Labor issues: demo, mogok kerja, kerusuhan
- Operations: satpam, patroli, pos jaga, pengawalan
- Regional: Jakarta, Surabaya, Bandung, Cikarang

### Reports (Bahasa Indonesia)
All security analysis in Indonesian using man guarding terminology:
- Analisis ancaman keamanan
- Tren kriminalitas
- Rekomendasi operasional
- Prosedur pos jaga dan patroli

## ⚡ Quick Actions

### Manually Trigger Crawl
1. Go to http://127.0.0.1:8000/scheduler/
2. Click **"Run Task"** button
3. View results in logs

### View Security Dashboard
1. Go to http://127.0.0.1:8000/dashboard/
2. See sentiment analysis
3. View trending security topics
4. Read LLM-generated reports in Bahasa Indonesia

### Check System Status
```bash
# View active tasks
python manage.py shell -c "from scheduler.models import CrawlTask; [print(f'{t.name}: Active={t.is_active}') for t in CrawlTask.objects.all()]"

# Check recent articles
python manage.py shell -c "from scraper.models import Article; print(f'Total articles: {Article.objects.count()}')"

# View Celery status
curl http://127.0.0.1:8000/scheduler/celery-status/
```

## 🔧 Configuration

### Update Keywords
```bash
python update_keywords_man_guarding.py
```

### Update News Sources
```bash
python update_sources_man_guarding.py
```

### Reset Scheduler
```bash
python setup_simple_scheduler.py
```

## 📊 Default Admin Credentials
Create superuser first:
```bash
python manage.py createsuperuser
```

## 📖 Documentation

- **Full Configuration**: [MAN_GUARDING_CONFIGURATION.md](MAN_GUARDING_CONFIGURATION.md)
- **Scheduler Details**: [SCHEDULER_GUIDE.md](SCHEDULER_GUIDE.md)
- **General README**: [README.md](README.md)

## 🆘 Troubleshooting

### Services Not Running
```bash
# Check what's running
ps aux | grep celery
ps aux | grep redis

# Restart everything
./stop_server.sh
./start_server.sh
```

### No Articles Being Created
```bash
# Check scraper log
tail -f scraper.log

# Test manually
python manage.py shell -c "from scraper.tasks import scrape_news_source; scrape_news_source(6)"
```

### Dashboard Empty
```bash
# Run manual crawl first
# Go to http://127.0.0.1:8000/scheduler/
# Click "Run Task" on "Crawl Berita Indonesia"
# Wait 2-3 minutes
# Refresh dashboard
```

## ✅ Verification Checklist

After starting services:

- [ ] Visit scheduler: http://127.0.0.1:8000/scheduler/
- [ ] Check Celery status shows **green** (worker & beat running)
- [ ] Click "Run Task" to test crawling
- [ ] Check logs show "Created article" messages
- [ ] Visit dashboard: http://127.0.0.1:8000/dashboard/
- [ ] Verify articles appear
- [ ] Check LLM analysis is in Bahasa Indonesia

## 💡 Tips

1. **First run**: Manually trigger "Crawl Berita Indonesia" to populate initial data
2. **Logs**: Check `celery_worker.log` and `scraper.log` for debugging
3. **Keywords**: Customize in `update_keywords_man_guarding.py` for specific needs
4. **Frequency**: Hourly crawl is usually sufficient for most operations

## 🎯 Quick Test

```bash
# 1. Start services
./start_server.sh

# 2. Wait 30 seconds for services to start

# 3. Open browser
open http://127.0.0.1:8000/scheduler/

# 4. Click "Run Task" on first task

# 5. Wait 2-3 minutes

# 6. Check dashboard
open http://127.0.0.1:8000/dashboard/
```

---

**System Status**: ✓ Configured for Indonesian man guarding services
**Language**: Bahasa Indonesia
**Keywords**: 105 active
**Sources**: 18 Indonesian news sources
**Tasks**: 2 active (hourly + daily)
