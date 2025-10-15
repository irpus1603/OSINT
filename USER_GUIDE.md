# OSINT Dashboard User Guide

## Getting Started

### Prerequisites
- Python 3.8 or higher
- pip package manager
- Git (for version control)

### Installation

1. Clone the repository:
   ```
   git clone <repository-url>
   cd osint-dashboard
   ```

2. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Run database migrations:
   ```
   python manage.py migrate
   ```

5. Create a superuser account:
   ```
   python manage.py createsuperuser
   ```

6. Populate initial data:
   ```
   python populate_data.py
   python create_sample_data.py
   ```

7. Run sentiment analysis on sample data:
   ```
   python analyze_sentiment.py
   ```

8. Create sample crawl tasks:
   ```
   python create_crawl_tasks.py
   ```

### Starting the Server

Run the development server:
```
python manage.py runserver
```

Or use the provided script:
```
./start_server.sh
```

The dashboard will be accessible at: http://127.0.0.1:8000/
The admin interface will be accessible at: http://127.0.0.1:8000/admin/

## Using the Dashboard

### Login
1. Navigate to http://127.0.0.1:8000/admin/
2. Enter the superuser credentials created during setup
3. Access the dashboard at http://127.0.0.1:8000/dashboard/

### Dashboard Sections

#### 1. Overview
- Shows key metrics including total articles/posts, sentiment distribution, and trending topics
- Allows filtering by date range (last 24 hours, 7 days, 30 days, or custom range)

#### 2. Sentiment Analysis
- Displays sentiment trends over time
- Shows sentiment distribution by source
- Provides detailed sentiment analysis of content

#### 3. Sources
- Lists all configured sources with content volume and sentiment data
- Allows comparison of source performance
- Shows source type distribution (news vs. social media)

#### 4. Alerts
- Configures and manages alert rules
- Shows active alerts
- Allows creation of new alerts based on sentiment, volume, or keywords

### Admin Interface

The Django admin interface provides management capabilities for:
- Sources (news and social media sources)
- Keywords (security-related terms for filtering)
- Articles and Posts (collected content)
- Sentiment Analysis (results of sentiment processing)
- Crawl Tasks (scheduled scraping tasks)
- Users and Permissions
- Dashboard Configurations

Access the admin interface at: http://127.0.0.1:8000/admin/

## Customization

### Adding New Sources
1. Navigate to the admin interface
2. Go to "Scraper" -> "Sources"
3. Click "Add Source"
4. Fill in the name, URL, and source type
5. Set "Is active" to True
6. Save the source

### Adding New Keywords
1. Navigate to the admin interface
2. Go to "Scraper" -> "Keywords"
3. Click "Add Keyword"
4. Enter the keyword term
5. Set "Is active" to True
6. Save the keyword

### Configuring Crawl Tasks
1. Navigate to the admin interface
2. Go to "Scheduler" -> "Crawl tasks"
3. Click "Add Crawl Task"
4. Configure the task name, source, keywords, and frequency
5. Set "Is active" to True
6. Save the task

## API Access

The system provides a REST API for programmatic access to data:
- Articles endpoint: `/api/articles/`
- Posts endpoint: `/api/posts/`
- Sentiment data endpoint: `/api/sentiment/`
- Sources endpoint: `/api/sources/`

API documentation can be accessed through the Django REST Framework interface.

## Maintenance

### Regular Tasks
1. Run sentiment analysis on new content:
   ```
   python analyze_sentiment.py
   ```

2. Check crawl task logs in the admin interface
3. Monitor system performance and database size
4. Update dependencies regularly:
   ```
   pip install --upgrade -r requirements.txt
   ```

### Backup and Recovery
1. Regularly backup the database file (`db.sqlite3` in development)
2. For production environments, implement proper database backup procedures
3. Keep copies of the `media` directory if file uploads are enabled

## Troubleshooting

### Common Issues

1. **Server won't start**: Check that all dependencies are installed and the database is accessible.

2. **No data showing in dashboard**: Ensure that:
   - Sources are configured and active
   - Keywords are defined
   - Crawl tasks are set up and running
   - Sentiment analysis has been run on the data

3. **Permission errors**: Verify that the user account has appropriate permissions in the admin interface.

### Getting Help

For issues not covered in this guide:
1. Check the Django logs for error messages
2. Review the application documentation in `README.md` and `PRD.md`
3. Contact the development team for support

## Next Steps

To extend the functionality of the OSINT dashboard:
1. Implement additional data sources (forums, dark web, etc.)
2. Add machine learning for threat prediction
3. Enhance visualization capabilities
4. Implement real-time data processing
5. Add mobile-responsive design
6. Integrate with external security tools and platforms