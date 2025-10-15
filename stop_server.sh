#!/bin/bash
# stop_server.sh
# Script to stop all OSINT dashboard services

echo "========================================="
echo "Stopping OSINT Dashboard Services"
echo "========================================="

# Stop Celery worker
echo "→ Stopping Celery worker..."
pkill -f "celery worker"
rm -f /tmp/celeryworker.pid

# Stop Celery beat
echo "→ Stopping Celery beat scheduler..."
pkill -f "celery beat"
rm -f /tmp/celerybeat.pid

# Stop Django server
echo "→ Stopping Django server..."
pkill -f "manage.py runserver"

# Optionally stop Redis (commented out by default to avoid affecting other services)
# Uncomment the lines below if you want to stop Redis as well
# echo "→ Stopping Redis server..."
# redis-cli shutdown

sleep 2

echo "========================================="
echo "✓ All services stopped"
echo "========================================="
