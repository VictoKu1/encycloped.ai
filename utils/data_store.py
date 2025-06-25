"""
Data Store Utilities
Handles persistent data storage and topic lifecycle management using PostgreSQL.
"""

from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from utils import db


def is_topic_outdated(generated_at_str):
    """Check if the topic is older than one month."""
    try:
        generated_at = datetime.strptime(generated_at_str, "%Y-%m-%dT%H:%M:%S")
    except Exception:
        return True  # If date is missing or invalid, treat as outdated
    return datetime.utcnow() - generated_at > timedelta(days=30)


def get_topic_data(topic_key):
    """Get topic data from the database."""
    topic = db.get_topic(topic_key)
    if not topic:
        return None
    # Convert generated_at to string for compatibility
    topic['generated_at'] = topic['generated_at'].strftime("%Y-%m-%dT%H:%M:%S")
    return topic


def save_topic_data(topic_key, content, markdown_content, subtopics=None):
    """Save topic data to the database."""
    db.save_topic(topic_key, content, markdown_content)


def update_topic_content(topic_key, content, markdown_content=None):
    """Update existing topic content in the database."""
    topic = db.get_topic(topic_key)
    if topic:
        db.save_topic(topic_key, content, markdown_content or topic.get('markdown'))


def get_markdown_from_html(html_content):
    """Extract plain text from HTML content for LLM processing."""
    soup = BeautifulSoup(html_content, "html.parser")
    return soup.get_text(" ")


def topic_exists(topic_key):
    """Check if a topic exists in the database."""
    return db.get_topic(topic_key) is not None


def get_all_topics():
    """Get all topics from the database."""
    return db.get_all_topics()


def clear_data_store():
    """Not implemented: Clearing the database is not supported in production."""
    pass 