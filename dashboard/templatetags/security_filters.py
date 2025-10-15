from django import template
from django.utils.safestring import mark_safe
import re
import html

register = template.Library()

@register.filter
def format_security_analysis(value):
    """
    Convert LLM-generated content to properly formatted HTML for display
    """
    if not value:
        return ""
    
    # First, escape any existing HTML to prevent XSS
    text = html.escape(str(value))
    
    # Convert common markdown-like patterns to HTML
    # Bold text: **text** or __text__
    text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'__(.*?)__', r'<strong>\1</strong>', text)
    
    # Italic text: *text* or _text_
    text = re.sub(r'(?<!\*)\*([^*]+)\*(?!\*)', r'<em>\1</em>', text)
    text = re.sub(r'(?<!_)_([^_]+)_(?!_)', r'<em>\1</em>', text)
    
    # Headers
    text = re.sub(r'^### (.*?)$', r'<h3>\1</h3>', text, flags=re.MULTILINE)
    text = re.sub(r'^## (.*?)$', r'<h2>\1</h2>', text, flags=re.MULTILINE)
    text = re.sub(r'^# (.*?)$', r'<h1>\1</h1>', text, flags=re.MULTILINE)
    
    # Lists - convert lines starting with - or * to list items
    lines = text.split('\n')
    in_list = False
    processed_lines = []
    
    for line in lines:
        stripped = line.strip()
        
        # Check if this line is a list item
        if stripped.startswith('- ') or stripped.startswith('* '):
            if not in_list:
                processed_lines.append('<ul>')
                in_list = True
            # Remove the bullet and wrap in <li>
            item_text = stripped[2:].strip()
            processed_lines.append(f'<li>{item_text}</li>')
        
        # Check for numbered lists
        elif re.match(r'^\d+\.\s+', stripped):
            if not in_list:
                processed_lines.append('<ol>')
                in_list = True
            # Remove the number and wrap in <li>
            item_text = re.sub(r'^\d+\.\s+', '', stripped)
            processed_lines.append(f'<li>{item_text}</li>')
        
        else:
            # Not a list item
            if in_list:
                # Close any open list
                if any('ul>' in pl for pl in processed_lines[-5:]):
                    processed_lines.append('</ul>')
                elif any('ol>' in pl for pl in processed_lines[-5:]):
                    processed_lines.append('</ol>')
                in_list = False
            
            # Add regular line
            if stripped:
                processed_lines.append(f'<p>{line}</p>')
            else:
                processed_lines.append('<br>')
    
    # Close any remaining open list
    if in_list:
        if any('ul>' in pl for pl in processed_lines[-10:]):
            processed_lines.append('</ul>')
        elif any('ol>' in pl for pl in processed_lines[-10:]):
            processed_lines.append('</ol>')
    
    # Join lines back together
    text = '\n'.join(processed_lines)
    
    # Convert double line breaks to paragraph breaks
    text = re.sub(r'\n\s*\n', '</p>\n<p>', text)
    
    # Wrap content in paragraphs if not already wrapped
    if not text.startswith('<'):
        text = f'<p>{text}</p>'
    
    # Clean up any empty paragraphs
    text = re.sub(r'<p>\s*</p>', '', text)
    text = re.sub(r'<p>\s*<br>\s*</p>', '', text)
    
    return mark_safe(text)


@register.filter
def clean_llm_html(value):
    """
    Process and clean LLM-generated HTML content for safe display
    Properly handles markdown-formatted text from LLM responses
    """
    if not value:
        return ""

    text = str(value).strip()

    # If the content already has HTML tags, process them
    if '<' in text and '>' in text and not text.startswith('[') and not text.startswith('{'):
        # Clean up common HTML formatting issues
        text = text.replace('<p></p>', '')
        text = text.replace('<p> </p>', '')
        text = text.replace('<br><br>', '<br>')

        # Ensure proper paragraph spacing
        text = re.sub(r'</p>\s*<p>', '</p>\n<p>', text)
        text = re.sub(r'</h([1-6])>\s*<p>', r'</h\1>\n<p>', text)
        text = re.sub(r'</ul>\s*<p>', '</ul>\n<p>', text)
        text = re.sub(r'</ol>\s*<p>', '</ol>\n<p>', text)

        return mark_safe(text)
    else:
        # If no HTML tags, use the markdown-style formatter
        # This handles raw markdown text from LLM
        return format_security_analysis(text)