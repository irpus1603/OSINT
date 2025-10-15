# OSINT Dashboard Scheduler

The OSINT Dashboard includes a comprehensive task scheduling system for automated data collection.

## Architecture

The scheduler consists of several components:

1. **CrawlTask Model** - Database model for defining scheduled tasks
2. **CrawlLog Model** - Database model for tracking task execution
3. **Celery Tasks** - Asynchronous task execution using Celery
4. **Periodic Tasks** - Automated scheduling using Celery Beat
5. **Web Dashboard** - UI for managing and monitoring tasks
6. **Management Commands** - CLI tools for task initialization

## Scheduled Tasks

### Default Tasks
The system comes with three predefined tasks:

1. **Hourly News Crawl** - Scrapes news sources every hour
2. **Daily Social Media Crawl** - Scrapes social media sources daily
3. **Weekly Security News Crawl** - Comprehensive weekly security news crawl

### Task Configuration
Each task has the following properties:
- **Name**: Descriptive name for the task
- **Source**: Data source to crawl (news or social media)
- **Frequency**: How often to run (hourly, daily, weekly)
- **Status**: Current state (pending, running, completed, failed)
- **Last Run**: When the task was last executed
- **Next Run**: When the task is scheduled to run next
- **Active**: Whether the task is enabled

## Running the Scheduler

### Prerequisites
1. Redis server must be running
2. Celery worker must be started
3. Celery beat scheduler must be started

### Starting Services
```bash
# Start Redis server
redis-server

# Start Celery worker
celery -A osint_dashboard worker --loglevel=info

# Start Celery beat scheduler
celery -A osint_dashboard beat --loglevel=info
```

### Background Services
```bash
# Start services in background
redis-server --daemonize yes
celery -A osint_dashboard worker --loglevel=info --detach
celery -A osint_dashboard beat --loglevel=info --detach
```

## Management Commands

### Initialize Default Tasks
```bash
python manage.py init_crawl_tasks
```

### Manual Task Execution
```bash
# Run specific task by ID
curl -X POST http://127.0.0.1:8000/scheduler/run-task/1/

# Run all scheduled tasks
curl -X POST http://127.0.0.1:8000/scheduler/run-scheduled/
```

## Web Interface

### Scheduler Dashboard
Access the scheduler dashboard at: http://127.0.0.1:8000/scheduler/

Features:
- View all scheduled tasks
- See task status and schedules
- Manually run tasks
- View execution logs
- Monitor task performance

### Task Management
- **Run Now**: Execute a task immediately
- **Run All**: Execute all scheduled tasks
- **Status Monitoring**: Real-time task status updates
- **Log Tracking**: Detailed execution logs

## API Endpoints

### Task Execution
- `POST /scheduler/run-task/<task_id>/` - Run specific task
- `POST /scheduler/run-scheduled/` - Run all scheduled tasks
- `POST /scheduler/update-schedule/<task_id>/` - Update task schedule

### Response Format
All API endpoints return JSON responses:
```json
{
  "status": "success|error",
  "message": "Descriptive message",
  "task_id": "Celery task ID (if applicable)"
}
```

## Task Execution Flow

1. **Scheduled Execution**: Celery Beat triggers periodic tasks
2. **Task Selection**: System identifies tasks ready to run
3. **Log Creation**: Execution log entry is created
4. **Task Dispatch**: Appropriate scraping task is queued
5. **Status Update**: Task status and schedule are updated
6. **Log Completion**: Execution log is finalized

## Error Handling

### Common Issues
1. **Redis Connection**: Ensure Redis server is running
2. **Celery Worker**: Verify Celery worker is started
3. **Task Failures**: Check logs for specific error messages
4. **Network Issues**: Verify source URLs are accessible

### Monitoring
- Task status indicators (success, failed, running)
- Detailed error messages in logs
- Execution time tracking
- Item count tracking

## Customization

### Adding New Tasks
Tasks can be created through:
1. **Django Admin Interface**: http://127.0.0.1:8000/admin/scheduler/crawltask/
2. **Management Command**: Custom scripts
3. **Direct Database**: Programmatic creation

### Task Frequency
Supported frequencies:
- **Hourly**: Runs every hour
- **Daily**: Runs every day
- **Weekly**: Runs every week

### Source Types
- **News**: RSS feed scraping
- **Social**: Twitter API scraping

## Troubleshooting

### Service Status
```bash
# Check if Redis is running
redis-cli ping

# Check Celery processes
ps aux | grep celery
```

### Log Monitoring
```bash
# View Celery worker logs
tail -f celery.log

# View Celery beat logs
tail -f celerybeat.log
```

### Common Solutions
1. **Restart Services**: Stop and restart all services
2. **Check Permissions**: Ensure proper file permissions
3. **Update Schedules**: Reset task schedules if needed
4. **Clear Logs**: Clean old logs if disk space is an issue

## Best Practices

### Performance
- Limit concurrent tasks to avoid rate limiting
- Monitor system resources during execution
- Use appropriate delays between requests
- Implement proper error handling

### Security
- Secure API keys and credentials
- Limit access to scheduler dashboard
- Monitor for unusual activity
- Regular security updates

### Maintenance
- Regular database backups
- Log rotation for long-running systems
- Periodic task review and cleanup
- Performance monitoring and optimization