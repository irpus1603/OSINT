# OSINT Dashboard for Security Company

Open Source Intelligence (OSINT) dashboard for monitoring security threats and analyzing sentiment from news media and social media sources.

## Features

- News media scraping based on specific topics or keywords
- Social media scraping based on specific topics or keywords
- Scheduled data crawling with configurable frequencies
- Sentiment analysis dashboard
- Data visualization and insights
- Task scheduling and monitoring
- REST API for programmatic access

## Technologies

- Django (Backend)
- Django REST Framework (API)
- PostgreSQL (Database)
- Celery (Task Queue)
- Redis (Message Broker)
- Chart.js (Data Visualization)
- BeautifulSoup4 (Web Scraping)
- Tweepy (Twitter API)

## Setup

1. Create virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Create .env file with required environment variables:
   ```env
   DEBUG=True
   SECRET_KEY=your-secret-key
   DATABASE_URL=postgresql://user:password@localhost:5432/osint_db
   REDIS_URL=redis://localhost:6379/0
   TWITTER_BEARER_TOKEN=your-twitter-bearer-token
   ```

4. Run migrations:
   ```bash
   python manage.py migrate
   ```

5. Create superuser:
   ```bash
   python manage.py createsuperuser
   ```

6. Populate initial data:
   ```bash
   python populate_data.py
   python create_sample_data.py
   ```

7. Initialize crawl tasks:
   ```bash
   python manage.py init_crawl_tasks
   ```

8. Start development server:
   ```bash
   python manage.py runserver
   ```

## Project Structure

```
osint_dashboard/
├── osint_dashboard/          # Project settings
├── scraper/                 # Web scraping functionality
├── analyzer/                # Sentiment analysis and data processing
├── dashboard/               # Frontend dashboard and visualizations
├── scheduler/               # Scheduled tasks and crawlers
├── api/                     # REST API endpoints
├── static/                  # Static files (CSS, JS, Images)
├── templates/               # HTML templates
├── manage.py               # Django management script
└── requirements.txt        # Project dependencies
```

## Running Services

### Prerequisites
- Redis server must be running
- Database must be accessible

### Starting All Services
```bash
# Start Redis server
redis-server --daemonize yes

# Start Celery worker
celery -A osint_dashboard worker --loglevel=info --detach

# Start Celery beat scheduler
celery -A osint_dashboard beat --loglevel=info --detach

# Start Django development server
python manage.py runserver
```

## Access Points

- **Main Dashboard**: http://127.0.0.1:8000/dashboard/
- **Scheduler Dashboard**: http://127.0.0.1:8000/scheduler/
- **Admin Interface**: http://127.0.0.1:8000/admin/
- **API Endpoints**: http://127.0.0.1:8000/api/

## Default Scheduled Tasks

1. **Hourly News Crawl** - Scrapes news sources every hour
2. **Daily Social Media Crawl** - Scrapes social media sources daily
3. **Weekly Security News Crawl** - Comprehensive weekly security news crawl

## Management Commands

```bash
# Initialize default crawl tasks
python manage.py init_crawl_tasks

# Scrape all active sources
python manage.py scrape_sources

# Show scraping statistics
python manage.py scrape_sources --stats
```