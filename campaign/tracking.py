"""
Email tracking utilities for open and click tracking.
"""
import re
from urllib.parse import urlencode
from django.urls import reverse
from django.conf import settings


def add_tracking_pixel(html_body, tracking_id):
    """
    Add a 1x1 transparent tracking pixel to the email body.

    Args:
        html_body: The HTML email body
        tracking_id: The UUID tracking ID for the email

    Returns:
        Modified HTML with tracking pixel
    """
    tracking_url = f"{get_base_url()}{reverse('email_tracking_pixel', args=[tracking_id])}"
    pixel_html = f'<img src="{tracking_url}" alt="" width="1" height="1" style="display:none;" />'

    # Try to insert before closing body tag, otherwise append
    if '</body>' in html_body.lower():
        html_body = re.sub(r'</body>', f'{pixel_html}</body>', html_body, flags=re.IGNORECASE)
    else:
        html_body += pixel_html

    return html_body


def replace_links_with_tracking(html_body, tracking_id):
    """
    Replace all links in the email body with tracking URLs.

    Args:
        html_body: The HTML email body
        tracking_id: The UUID tracking ID for the email

    Returns:
        Modified HTML with tracking links
    """
    def replace_link(match):
        original_url = match.group(1)
        # Skip tracking pixel and other tracking URLs
        if 'track/pixel' in original_url or 'track/click' in original_url:
            return match.group(0)

        tracking_url = f"{get_base_url()}{reverse('email_tracking_click', args=[tracking_id])}"
        tracking_url += '?' + urlencode({'url': original_url})
        return f'href="{tracking_url}"'

    # Replace href attributes in anchor tags
    html_body = re.sub(r'href="([^"]+)"', replace_link, html_body)
    html_body = re.sub(r"href='([^']+)'", replace_link, html_body)

    return html_body


def get_base_url():
    """
    Get the base URL for the application.
    Uses SITE_URL from settings if available, otherwise constructs from request.
    """
    return getattr(settings, 'SITE_URL', 'http://localhost:8000')


def convert_to_html(text_body):
    """
    Convert plain text email to HTML with basic formatting.

    Args:
        text_body: Plain text email body

    Returns:
        HTML formatted email
    """
    # Check if already HTML
    if '<html' in text_body.lower() or '<body' in text_body.lower():
        return text_body

    # Convert plain text to HTML
    html_body = text_body.replace('\n', '<br>\n')
    html_body = f"""
    <html>
    <head>
        <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
    </head>
    <body>
        {html_body}
    </body>
    </html>
    """
    return html_body
