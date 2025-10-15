import os
import django
import json

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'osint_dashboard.settings')
django.setup()

from dashboard.views import dashboard_view
from django.http import HttpRequest

def test_dashboard_view():
    """
    Test the dashboard view function to see what data it returns
    """
    # Create a mock request object
    request = HttpRequest()
    
    # Call the dashboard view function
    response = dashboard_view(request)
    
    # Print the context data
    print("Dashboard view context data:")
    print(response.context_data)

if __name__ == '__main__':
    test_dashboard_view()