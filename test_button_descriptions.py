import os
import django

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'osint_dashboard.settings')
django.setup()

from django.template.loader import render_to_string
from django.http import HttpRequest

def test_button_descriptions():
    """Test that button descriptions are properly rendered"""
    print("Testing button descriptions...")
    
    # Create a mock request
    request = HttpRequest()
    request.META['HTTP_HOST'] = 'localhost:8000'
    
    # Mock context data
    context = {
        'tasks': [],
        'logs': [],
        'celery_status': {
            'worker_running': True,
            'beat_running': True,
            'celery_running': True
        }
    }
    
    try:
        # Render the template
        rendered = render_to_string('scheduler/dashboard.html', context, request=request)
        
        # Check for key elements
        checks = [
            ('Toolbar buttons', 'btn-toolbar'),
            ('Run All Tasks tooltip', 'data-bs-toggle="tooltip"'),
            ('Stop All Tasks tooltip', 'data-bs-toggle="tooltip"'),
            ('Start All Tasks tooltip', 'data-bs-toggle="tooltip"'),
            ('Stop Celery tooltip', 'data-bs-toggle="tooltip"'),
            ('Start Celery tooltip', 'data-bs-toggle="tooltip"'),
            ('Task buttons', 'btn-group'),
            ('Run Now tooltip', 'data-bs-toggle="tooltip"'),
            ('Enable/Disable tooltip', 'data-bs-toggle="tooltip"'),
            ('Reset Schedule tooltip', 'data-bs-toggle="tooltip"'),
        ]
        
        for check_name, check_text in checks:
            if check_text in rendered:
                print(f"✓ {check_name}: Found")
            else:
                print(f"✗ {check_name}: Not found")
        
        print("Button description test completed!")
        
    except Exception as e:
        print(f"Error testing button descriptions: {e}")

if __name__ == '__main__':
    test_button_descriptions()