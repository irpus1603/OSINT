#!/usr/bin/env python
"""
Simple test script for PDF generation
"""
import os
import sys
import django

# Add project root to path
sys.path.insert(0, '/Users/supriyadi/Projects/LLM/OSINT')

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'osint_dashboard.settings')
django.setup()

from weasyprint import HTML, CSS

# Simple HTML test
html_content = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Test PDF</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 2cm; }
        h1 { color: #2c3e50; }
    </style>
</head>
<body>
    <h1>OSINT Security Summary Test</h1>
    <p>This is a test PDF generation to verify WeasyPrint is working correctly.</p>
    <p>Current date: 2025-09-09</p>
</body>
</html>
"""

try:
    print("Generating test PDF...")
    pdf_bytes = HTML(string=html_content).write_pdf()
    
    with open('test_output.pdf', 'wb') as f:
        f.write(pdf_bytes)
    
    print(f"PDF generated successfully! Size: {len(pdf_bytes)} bytes")
    print("File saved as: test_output.pdf")

except Exception as e:
    print(f"Error generating PDF: {str(e)}")
    import traceback
    traceback.print_exc()