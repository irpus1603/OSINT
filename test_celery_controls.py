import os
import django

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'osint_dashboard.settings')
django.setup()

import subprocess

def test_celery_controls():
    """Test Celery process control functionality"""
    print("Testing Celery process controls...")
    
    # Check current Celery status
    try:
        # Check if Celery worker is running
        worker_check = subprocess.run(
            ['pgrep', '-f', 'celery.*worker'], 
            capture_output=True, 
            text=True
        )
        worker_running = worker_check.returncode == 0
        print(f"Celery worker running: {worker_running}")
        
        # Check if Celery beat is running
        beat_check = subprocess.run(
            ['pgrep', '-f', 'celery.*beat'], 
            capture_output=True, 
            text=True
        )
        beat_running = beat_check.returncode == 0
        print(f"Celery beat running: {beat_running}")
        
        print("Celery process control test completed!")
        
    except Exception as e:
        print(f"Error testing Celery controls: {e}")

if __name__ == '__main__':
    test_celery_controls()