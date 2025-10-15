import logging
from django.shortcuts import render
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .models import CrawlTask, CrawlLog
from scraper.models import Source
from scraper.tasks import scrape_news_source, scrape_social_media_source, run_scheduled_scraping
from datetime import timedelta
import json

# Set up logging
logger = logging.getLogger(__name__)

def scheduler_dashboard(request):
    """Display scheduler dashboard with tasks and logs"""
    logger.info("Loading scheduler dashboard")
    tasks = CrawlTask.objects.all().order_by('-created_at')
    logs = CrawlLog.objects.all().order_by('-created_at')[:50]
    
    # Get Celery process status
    try:
        import subprocess
        
        # Check if Celery worker is running
        worker_check = subprocess.run(
            ['pgrep', '-f', 'celery.*worker'], 
            capture_output=True, 
            text=True
        )
        worker_running = worker_check.returncode == 0
        
        # Check if Celery beat is running
        beat_check = subprocess.run(
            ['pgrep', '-f', 'celery.*beat'], 
            capture_output=True, 
            text=True
        )
        beat_running = beat_check.returncode == 0
        
        celery_status = {
            'worker_running': worker_running,
            'beat_running': beat_running,
            'celery_running': worker_running and beat_running
        }
    except Exception as e:
        logger.error(f"Error checking Celery status: {e}")
        celery_status = {
            'worker_running': False,
            'beat_running': False,
            'celery_running': False
        }
    
    context = {
        'tasks': tasks,
        'logs': logs,
        'celery_status': celery_status
    }
    logger.info(f"Loaded scheduler dashboard with {tasks.count()} tasks and {logs.count()} logs")
    return render(request, 'scheduler/dashboard.html', context)

@require_http_methods(["POST"])
@csrf_exempt
def run_task(request, task_id):
    """Manually run a specific crawl task"""
    logger.info(f"Manually running crawl task ID: {task_id}")
    try:
        task = CrawlTask.objects.get(id=task_id, is_active=True)
        logger.info(f"Found task: {task.name} (Source: {task.source.name})")
        
        # Create log entry
        log = CrawlLog.objects.create(
            task=task,
            started_at=timezone.now(),
            status='running'
        )
        logger.info(f"Created log entry for task {task.name}")
        
        # Run the appropriate scraping task
        if task.source.source_type == 'news':
            logger.info(f"Queueing news scraping task for {task.source.name}")
            result = scrape_news_source.delay(task.source.id)
        elif task.source.source_type == 'social':
            logger.info(f"Queueing social media scraping task for {task.source.name}")
            result = scrape_social_media_source.delay(task.source.id)
        else:
            error_msg = f"Unsupported source type: {task.source.source_type}"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        # Update task
        task.last_run = timezone.now()
        task.status = 'running'
        task.save()
        logger.info(f"Updated task {task.name} status to running")
        
        success_msg = f'Task {task.name} started successfully'
        logger.info(success_msg)
        return JsonResponse({
            'status': 'success',
            'message': success_msg,
            'task_id': str(result.id)
        })
        
    except CrawlTask.DoesNotExist:
        error_msg = 'Task not found or inactive'
        logger.warning(error_msg)
        return JsonResponse({
            'status': 'error',
            'message': error_msg
        }, status=404)
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Error running task {task_id}: {error_msg}")
        return JsonResponse({
            'status': 'error',
            'message': error_msg
        }, status=500)

@require_http_methods(["POST"])
@csrf_exempt
def run_scheduled_tasks(request):
    """Run all scheduled tasks"""
    logger.info("Running all scheduled tasks")
    try:
        result = run_scheduled_scraping.delay()
        success_msg = 'Scheduled scraping started'
        logger.info(success_msg)
        return JsonResponse({
            'status': 'success',
            'message': success_msg,
            'task_id': str(result.id)
        })
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Error running scheduled tasks: {error_msg}")
        return JsonResponse({
            'status': 'error',
            'message': error_msg
        }, status=500)

def calculate_next_run(frequency, last_run=None):
    """Calculate next run time based on frequency"""
    if last_run is None:
        last_run = timezone.now()
        
    if frequency == 'hourly':
        return last_run + timedelta(hours=1)
    elif frequency == 'daily':
        return last_run + timedelta(days=1)
    elif frequency == 'weekly':
        return last_run + timedelta(weeks=1)
    else:
        # Default to daily
        return last_run + timedelta(days=1)

@require_http_methods(["POST"])
@csrf_exempt
def update_task_schedule(request, task_id):
    """Update a task's schedule"""
    logger.info(f"Updating schedule for task ID: {task_id}")
    try:
        task = CrawlTask.objects.get(id=task_id)
        
        # Update next run time
        task.next_run = calculate_next_run(task.frequency)
        task.save()
        logger.info(f"Updated schedule for task {task.name}")
        
        return JsonResponse({
            'status': 'success',
            'message': f'Task {task.name} schedule updated',
            'next_run': task.next_run.isoformat()
        })
    except CrawlTask.DoesNotExist:
        error_msg = 'Task not found'
        logger.warning(error_msg)
        return JsonResponse({
            'status': 'error',
            'message': error_msg
        }, status=404)
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Error updating task schedule {task_id}: {error_msg}")
        return JsonResponse({
            'status': 'error',
            'message': error_msg
        }, status=500)

@require_http_methods(["POST"])
@csrf_exempt
def toggle_task_status(request, task_id):
    """Enable or disable a task"""
    logger.info(f"Toggling status for task ID: {task_id}")
    try:
        task = CrawlTask.objects.get(id=task_id)
        
        # Toggle the active status
        task.is_active = not task.is_active
        task.save()
        status_text = "enabled" if task.is_active else "disabled"
        logger.info(f"Task {task.name} has been {status_text}")
        
        return JsonResponse({
            'status': 'success',
            'message': f'Task {task.name} has been {status_text}',
            'is_active': task.is_active
        })
    except CrawlTask.DoesNotExist:
        error_msg = 'Task not found'
        logger.warning(error_msg)
        return JsonResponse({
            'status': 'error',
            'message': error_msg
        }, status=404)
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Error toggling task status {task_id}: {error_msg}")
        return JsonResponse({
            'status': 'error',
            'message': error_msg
        }, status=500)

@require_http_methods(["POST"])
@csrf_exempt
def reset_task_schedule(request, task_id):
    """Reset a task's schedule to default"""
    logger.info(f"Resetting schedule for task ID: {task_id}")
    try:
        task = CrawlTask.objects.get(id=task_id)
        
        # Reset schedule based on frequency
        task.next_run = calculate_next_run(task.frequency)
        task.last_run = None
        task.status = 'pending'
        task.save()
        logger.info(f"Task {task.name} schedule has been reset")
        
        return JsonResponse({
            'status': 'success',
            'message': f'Task {task.name} schedule has been reset',
            'next_run': task.next_run.isoformat() if task.next_run else None
        })
    except CrawlTask.DoesNotExist:
        error_msg = 'Task not found'
        logger.warning(error_msg)
        return JsonResponse({
            'status': 'error',
            'message': error_msg
        }, status=404)
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Error resetting task schedule {task_id}: {error_msg}")
        return JsonResponse({
            'status': 'error',
            'message': error_msg
        }, status=500)

@require_http_methods(["POST"])
@csrf_exempt
def stop_all_tasks(request):
    """Disable all crawl tasks"""
    logger.info("Disabling all crawl tasks")
    try:
        # Disable all active tasks
        tasks = CrawlTask.objects.filter(is_active=True)
        count = tasks.update(is_active=False)
        logger.info(f"Disabled {count} tasks")
        
        return JsonResponse({
            'status': 'success',
            'message': f'Successfully disabled {count} tasks',
            'disabled_count': count
        })
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Error stopping all tasks: {error_msg}")
        return JsonResponse({
            'status': 'error',
            'message': error_msg
        }, status=500)

@require_http_methods(["POST"])
@csrf_exempt
def start_all_tasks(request):
    """Enable all crawl tasks"""
    logger.info("Enabling all crawl tasks")
    try:
        # Enable all tasks
        tasks = CrawlTask.objects.all()
        count = tasks.update(is_active=True)
        logger.info(f"Enabled {count} tasks")
        
        return JsonResponse({
            'status': 'success',
            'message': f'Successfully enabled {count} tasks',
            'enabled_count': count
        })
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Error starting all tasks: {error_msg}")
        return JsonResponse({
            'status': 'error',
            'message': error_msg
        }, status=500)

@require_http_methods(["POST"])
@csrf_exempt
def stop_celery_processes(request):
    """Stop all Celery processes (worker and beat) and update task status"""
    logger.info("Stopping Celery processes")
    try:
        import subprocess
        import signal
        import os
        from django.utils import timezone
        from .models import CrawlTask, CrawlLog
        
        # Kill Celery worker processes
        worker_result = subprocess.run(['pkill', '-f', 'celery.*worker'], 
                                     capture_output=True, text=True)
        
        # Kill Celery beat processes
        beat_result = subprocess.run(['pkill', '-f', 'celery.*beat'], 
                                   capture_output=True, text=True)
        
        # Count processes killed
        workers_killed = 0 if 'No matching processes' in worker_result.stdout else worker_result.returncode
        beats_killed = 0 if 'No matching processes' in beat_result.stdout else beat_result.returncode
        
        # Update database status for running tasks
        # Update running tasks to failed status
        running_tasks = CrawlTask.objects.filter(status='running')
        running_tasks_updated = running_tasks.update(
            status='failed',
            last_run=timezone.now()
        )
        
        # Update running logs to failed status
        running_logs = CrawlLog.objects.filter(status='running')
        running_logs_updated = running_logs.update(
            status='failed',
            finished_at=timezone.now(),
            error_message='Celery processes stopped manually'
        )
        
        logger.info(f"Stopped Celery processes - Workers: {workers_killed}, Beat: {beats_killed}")
        logger.info(f"Updated {running_tasks_updated} tasks and {running_logs_updated} logs")
        
        return JsonResponse({
            'status': 'success',
            'message': f'Stopped Celery processes - Workers: {workers_killed}, Beat: {beats_killed}. Updated {running_tasks_updated} tasks and {running_logs_updated} logs.',
            'workers_killed': workers_killed,
            'beats_killed': beats_killed,
            'tasks_updated': running_tasks_updated,
            'logs_updated': running_logs_updated
        })
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Error stopping Celery processes: {error_msg}")
        return JsonResponse({
            'status': 'error',
            'message': error_msg
        }, status=500)

@require_http_methods(["POST"])
@csrf_exempt
def start_celery_processes(request):
    """Start Celery processes (worker and beat)"""
    logger.info("Starting Celery processes")
    try:
        import subprocess
        import os
        
        # Change to project directory
        project_dir = '/Users/supriyadi/Projects/LLM/OSINT'
        
        # Start Celery worker in background
        worker_cmd = [
            'celery', '-A', 'osint_dashboard', 'worker', 
            '--loglevel=info', '--detach'
        ]
        worker_result = subprocess.run(
            worker_cmd, 
            cwd=project_dir,
            capture_output=True, 
            text=True
        )
        
        # Start Celery beat in background
        beat_cmd = [
            'celery', '-A', 'osint_dashboard', 'beat', 
            '--loglevel=info', '--detach'
        ]
        beat_result = subprocess.run(
            beat_cmd, 
            cwd=project_dir,
            capture_output=True, 
            text=True
        )
        
        logger.info("Started Celery processes")
        return JsonResponse({
            'status': 'success',
            'message': 'Started Celery processes',
            'worker_status': worker_result.returncode,
            'beat_status': beat_result.returncode
        })
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Error starting Celery processes: {error_msg}")
        return JsonResponse({
            'status': 'error',
            'message': error_msg
        }, status=500)

@require_http_methods(["GET"])
@csrf_exempt
def get_celery_status(request):
    """Get status of Celery processes"""
    try:
        import subprocess
        
        # Check if Celery worker is running
        worker_check = subprocess.run(
            ['pgrep', '-f', 'celery.*worker'], 
            capture_output=True, 
            text=True
        )
        worker_running = worker_check.returncode == 0
        
        # Check if Celery beat is running
        beat_check = subprocess.run(
            ['pgrep', '-f', 'celery.*beat'], 
            capture_output=True, 
            text=True
        )
        beat_running = beat_check.returncode == 0
        
        logger.info(f"Celery status - Worker: {worker_running}, Beat: {beat_running}")
        return JsonResponse({
            'status': 'success',
            'worker_running': worker_running,
            'beat_running': beat_running,
            'celery_running': worker_running and beat_running
        })
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Error getting Celery status: {error_msg}")
        return JsonResponse({
            'status': 'error',
            'message': error_msg
        }, status=500)

@require_http_methods(["POST"])
@csrf_exempt
def cancel_running_task(request, task_id):
    """Cancel a running task and update its status"""
    logger.info(f"Cancelling running task ID: {task_id}")
    try:
        from django.utils import timezone
        from .models import CrawlTask, CrawlLog
        
        # Get the task
        task = CrawlTask.objects.get(id=task_id)
        
        # Update task status
        task.status = 'failed'
        task.last_run = timezone.now()
        task.save()
        
        # Update any running logs for this task
        running_logs = CrawlLog.objects.filter(task=task, status='running')
        running_logs.update(
            status='failed',
            finished_at=timezone.now(),
            error_message='Task cancelled manually'
        )
        
        logger.info(f"Cancelled task {task.name}")
        return JsonResponse({
            'status': 'success',
            'message': f'Task {task.name} has been cancelled and marked as failed'
        })
    except CrawlTask.DoesNotExist:
        error_msg = 'Task not found'
        logger.warning(error_msg)
        return JsonResponse({
            'status': 'error',
            'message': error_msg
        }, status=404)
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Error cancelling task {task_id}: {error_msg}")
        return JsonResponse({
            'status': 'error',
            'message': error_msg
        }, status=500)