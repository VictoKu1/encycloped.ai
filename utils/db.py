import os
import psycopg2
from psycopg2.extras import RealDictCursor

DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': int(os.getenv('DB_PORT', 5432)),
    'dbname': os.getenv('DB_NAME', 'encyclopedai'),
    'user': os.getenv('DB_USER', 'encyclo_user'),
    'password': os.getenv('DB_PASSWORD', 'encyclo_pass'),
}

def get_connection():
    return psycopg2.connect(**DB_CONFIG)

def init_db():
    """Initialize the database schema for topics and logs."""
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute('''
            CREATE TABLE IF NOT EXISTS topics (
                id SERIAL PRIMARY KEY,
                topic_key TEXT UNIQUE NOT NULL,
                content TEXT NOT NULL,
                markdown TEXT,
                generated_at TIMESTAMP NOT NULL DEFAULT NOW(),
                topic_suggestions JSONB
            );
            ''')
            cur.execute('''
            CREATE TABLE IF NOT EXISTS logs (
                id SERIAL PRIMARY KEY,
                event_time TIMESTAMP NOT NULL DEFAULT NOW(),
                event_type TEXT NOT NULL,
                details TEXT
            );
            ''')
        conn.commit()

def save_topic(topic_key, content, markdown, topic_suggestions=None):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute('''
                INSERT INTO topics (topic_key, content, markdown, generated_at, topic_suggestions)
                VALUES (%s, %s, %s, NOW(), %s)
                ON CONFLICT (topic_key) DO UPDATE SET
                    content = EXCLUDED.content,
                    markdown = EXCLUDED.markdown,
                    generated_at = NOW(),
                    topic_suggestions = EXCLUDED.topic_suggestions;
            ''', (topic_key, content, markdown, topic_suggestions))
        conn.commit()

def get_topic(topic_key):
    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute('SELECT * FROM topics WHERE topic_key = %s', (topic_key,))
            return cur.fetchone()

def get_all_topics():
    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute('SELECT topic_key FROM topics')
            return [row['topic_key'] for row in cur.fetchall()]

def log_event(event_type, details=None):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute('INSERT INTO logs (event_type, details) VALUES (%s, %s)', (event_type, details))
        conn.commit()

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Database utilities for encycloped.ai")
    parser.add_argument('--init', action='store_true', help='Initialize the database schema')
    args = parser.parse_args()
    if args.init:
        init_db()
        print("Database schema initialized successfully.") 