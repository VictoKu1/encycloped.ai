"""
Security Validators
Handles input validation, sanitization, and security measures.
"""

import re
import logging
from datetime import datetime
from werkzeug.exceptions import BadRequest
import bleach

# Topic slug validation regex
TOPIC_SLUG_REGEX = re.compile(r'^[a-zA-Z0-9_\-\s]{1,50}$')

# Configure allowed HTML tags and attributes
ALLOWED_TAGS = ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'ul', 'ol', 'li', 'strong', 'em', 'a', 'blockquote', 'code']
ALLOWED_ATTRIBUTES = {
    'a': ['href', 'title'],
    'h1': ['id'],
    'h2': ['id'],
    'h3': ['id'],
    'h4': ['id'],
    'h5': ['id'],
    'h6': ['id']
}


def validate_topic_slug(topic):
    """Validate topic slug against allowed pattern."""
    if not TOPIC_SLUG_REGEX.match(topic):
        raise BadRequest("Invalid topic name")
    return topic.lower()  # Convert to lowercase


def sanitize_html(html_content):
    """Sanitize HTML content using bleach."""
    return bleach.clean(
        html_content,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRIBUTES,
        strip=True
    )


def sanitize_text(text_content):
    """Sanitize plain text content."""
    return bleach.clean(text_content, tags=[], strip=True)


def sanitize_urls(urls):
    """Sanitize a list of URLs."""
    return [bleach.clean(url) for url in urls]


def log_contribution(ip, user_id, action, topic, details):
    """Log contribution metadata."""
    logging.info(
        f"Contribution - IP: {ip}, User: {user_id}, Action: {action}, "
        f"Topic: {topic}, Details: {details}, Time: {datetime.utcnow()}"
    )


def validate_json_payload(data, required_fields):
    """Validate JSON payload has all required fields."""
    if not data:
        raise BadRequest("Invalid JSON payload")
    
    if not all(field in data for field in required_fields):
        raise BadRequest(f"Missing required fields: {required_fields}")
    
    return True


def validate_rate_limit(request, limiter):
    """Validate rate limiting for requests."""
    # This is handled by Flask-Limiter decorators
    # This function can be used for custom rate limiting logic if needed
    pass 