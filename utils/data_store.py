"""
Data Store Utilities
Handles in-memory data storage and topic lifecycle management.
"""

from datetime import datetime, timedelta
from bs4 import BeautifulSoup


# A simple in-memory datastore for demo purposes.
data_store = {}  # e.g., {'Python': {'content': '...', 'subtopics': {...}, 'generated_at': datetime, 'markdown': '...'}}


def is_topic_outdated(generated_at_str):
    """Check if the topic is older than one month."""
    try:
        generated_at = datetime.strptime(generated_at_str, "%Y-%m-%dT%H:%M:%S")
    except Exception:
        return True  # If date is missing or invalid, treat as outdated
    return datetime.utcnow() - generated_at > timedelta(days=30)


def get_topic_data(topic_key):
    """Get topic data from the data store."""
    return data_store.get(topic_key)


def save_topic_data(topic_key, content, markdown_content, subtopics=None):
    """Save topic data to the data store."""
    now_str = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S")
    data_store[topic_key] = {
        "content": content,
        "subtopics": subtopics or {},
        "generated_at": now_str,
        "markdown": markdown_content
    }


def update_topic_content(topic_key, content, markdown_content=None):
    """Update existing topic content."""
    if topic_key in data_store:
        data_store[topic_key]["content"] = content
        if markdown_content:
            data_store[topic_key]["markdown"] = markdown_content
        data_store[topic_key]["generated_at"] = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S")


def get_markdown_from_html(html_content):
    """Extract plain text from HTML content for LLM processing."""
    soup = BeautifulSoup(html_content, "html.parser")
    return soup.get_text(" ")


def topic_exists(topic_key):
    """Check if a topic exists in the data store."""
    return topic_key in data_store


def get_all_topics():
    """Get all topics from the data store."""
    return list(data_store.keys())


def clear_data_store():
    """Clear the data store (useful for testing)."""
    global data_store
    data_store = {} 