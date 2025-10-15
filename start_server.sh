#!/bin/bash
# start_server.sh
# Script to start all OSINT dashboard services

echo "========================================="
echo "Starting OSINT Dashboard Services"
echo "========================================="

# Note: Redis is managed via Docker
# Make sure Redis container is running before starting services

# Stop existing Celery processes if any
echo "→ Stopping existing Celery processes..."
pkill -f "celery worker" 2>/dev/null
pkill -f "celery beat" 2>/dev/null
sleep 2

# Start Celery worker
echo "→ Starting Celery worker..."
celery -A osint_dashboard worker --loglevel=info --detach --pidfile=/tmp/celeryworker.pid --logfile=celery_worker.log
sleep 3

# Start Celery beat scheduler
echo "→ Starting Celery beat scheduler..."
celery -A osint_dashboard beat --loglevel=info --detach --pidfile=/tmp/celerybeat.pid --logfile=celery_beat.log
sleep 2

echo "========================================="
echo "✓ All background services started"
echo "========================================="
echo ""
echo "→ Starting Django development server..."
echo ""
echo "Access points:"
echo "  • Main Dashboard: http://127.0.0.1:8000/dashboard/"
echo "  • Scheduler: http://127.0.0.1:8000/scheduler/"
echo "  • Admin: http://127.0.0.1:8000/admin/"
echo "  • API: http://127.0.0.1:8000/api/"
echo ""
echo "Logs:"
echo "  • Celery worker: celery_worker.log"
echo "  • Celery beat: celery_beat.log"
echo ""
echo "Press Ctrl+C to stop the Django server"
echo "To stop all services, run: ./stop_server.sh"
echo "========================================="

# Start Django server (this runs in foreground)
python manage.py runserver