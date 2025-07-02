"""
Main Flask Application
AI Moderated Encyclopedia - Main application entry point.
"""

import os
import sys
import logging
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from werkzeug.exceptions import BadRequest
import hashlib

# Import from our modular packages
from agents.topic_generator import (
    generate_topic_content, 
    update_topic_content, 
    extract_topic_suggestions,
    process_user_feedback,
    set_llm_mode
)
from security.validators import (
    validate_topic_slug, 
    sanitize_text, 
    sanitize_urls, 
    log_contribution,
    validate_json_payload
)
from content.markdown_processor import (
    convert_markdown, 
    remove_duplicate_header, 
    linkify_topics
)
from utils import db
from utils.data_store import (
    is_topic_outdated, 
    get_topic_data, 
    save_topic_data, 
    update_topic_content as update_store_content,
    get_markdown_from_html,
    topic_exists
)

# Configure logging
logging.basicConfig(
    filename='app.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY', os.urandom(24))
# Configure Flask-Limiter to use Redis as storage backend for rate limiting
redis_host = os.environ.get('REDIS_HOST', 'localhost')
app.config['RATELIMIT_STORAGE_URI'] = f'redis://{redis_host}:6379/0'

# Initialize rate limiter
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

db.init_db()  # Initialize the database schema at startup


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        topic = request.form.get("topic", "").strip()
        if topic:
            try:
                topic = validate_topic_slug(topic)
                return redirect(url_for("topic_page", topic=topic))
            except BadRequest as e:
                return str(e), 400
    return render_template("index.html")


@app.route("/<topic>", methods=["GET"])
def topic_page(topic):
    try:
        topic = validate_topic_slug(topic.strip())
        topic_key = topic.lower()
        now_str = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S")
        topic_data = get_topic_data(topic_key)
        gen_at = topic_data.get('generated_at') if topic_data else None
        is_outdated = is_topic_outdated(gen_at) if gen_at else True

        # Default values
        markdown_content = None
        html_content = None
        last_update = now_str
        topic_suggestions = []
        ambiguous_meanings = None
        ambiguous = False

        if not topic_data:
            logging.info(f"[DEBUG] Will call OpenAI: topic_data is None (topic not in DB)")
            reply_code, markdown_content = generate_topic_content(topic)
            if reply_code.strip() == "45":
                ambiguous = True
                raw = markdown_content.strip()
                lines = [line.strip() for line in raw.splitlines() if line.strip()]
                intro = lines[0] if lines else f"The topic {topic.title()} may have several meanings, did you mean:"
                options = [l for l in lines[1:] if l and l[0].isdigit() and '.' in l]
                # Remove numbering and extra spaces
                ambiguous_meanings = [l.split('.', 1)[1].strip() if '.' in l else l for l in options]
                return render_template("topic.html", topic=topic.title(), content=None, last_update=now_str, ambiguous=True, ambiguous_intro=intro, ambiguous_meanings=ambiguous_meanings)
            else:
                topic_suggestions = extract_topic_suggestions(markdown_content)
                html_content = convert_markdown(linkify_topics(markdown_content, topic_suggestions))
                save_topic_data(topic_key, html_content, markdown_content, topic_suggestions)
                last_update = now_str
                topic_data = get_topic_data(topic_key)
        elif is_outdated:
            logging.info(f"[DEBUG] Will call OpenAI: topic is outdated")
            current_content = topic_data["content"]
            reply_code, updated_content = update_topic_content(topic, current_content)
            if reply_code.strip() == "1":
                # Regenerate markdown and topic suggestions
                markdown_content = updated_content
                topic_suggestions = extract_topic_suggestions(markdown_content)
                html_content = convert_markdown(linkify_topics(markdown_content, topic_suggestions))
                save_topic_data(topic_key, html_content, markdown_content, topic_suggestions)
                last_update = now_str
                topic_data = get_topic_data(topic_key)
            elif reply_code.strip() == "45":
                ambiguous = True
                raw = updated_content.strip()
                if '\n' in raw:
                    lines = [line.strip() for line in raw.splitlines() if line.strip()]
                else:
                    parts = raw.split(') ')
                    lines = []
                    for part in parts:
                        if part:
                            if not part.endswith(')'):
                                part = part + ')'
                            lines.append(part.strip())
                ambiguous_meanings = [l for l in lines if l and l != '45']
                html_content = "<ul>" + "".join([f'<li><a href="/{m.replace(" ", "%20")}">{m}</a></li>' for m in ambiguous_meanings]) + "</ul>"
                save_topic_data(topic_key, html_content, updated_content, [])
                last_update = now_str
                topic_data = get_topic_data(topic_key)
        else:
            logging.info(f"[DEBUG] Will NOT call OpenAI: topic is present and not outdated")
            last_update = topic_data.get("generated_at", now_str)
            topic_suggestions = topic_data.get("topic_suggestions", [])

        # Use only the data from the database for rendering
        content = topic_data["content"]
        markdown_content = topic_data.get("markdown", None)
        ambiguous = False
        ambiguous_meanings = None
        if markdown_content and markdown_content.strip() and markdown_content.strip().split("\n", 1)[0].strip() == "45":
            ambiguous = True
            raw = markdown_content.strip()
            if '\n' in raw:
                lines = [line.strip() for line in raw.splitlines()[1:] if line.strip()]
            else:
                parts = raw.split(') ')
                lines = []
                for part in parts:
                    if part:
                        if not part.endswith(')'):
                            part = part + ')'
                        lines.append(part.strip())
            ambiguous_meanings = [l for l in lines if l and l != '45']

        if ambiguous:
            intro = ambiguous_intro if 'ambiguous_intro' in locals() else f"The topic {topic.title()} may have several meanings, did you mean:"
            return render_template("topic.html", topic=topic.title(), content=None, last_update=last_update, ambiguous=True, ambiguous_intro=intro, ambiguous_meanings=ambiguous_meanings)

        if not markdown_content:
            # If markdown is missing, show an error message
            html_content_final = '<p><em>Error: Article markdown missing. Please regenerate the article.</em></p>'
            return render_template("topic.html", topic=topic.title(), content=html_content_final, last_update=last_update, topic_suggestions=topic_suggestions)

        # Only linkify using the topic_suggestions from DB or just generated
        topic_suggestions = sorted(topic_suggestions, key=lambda x: -len(x)) if topic_suggestions else []
        filtered = []
        for i, s in enumerate(topic_suggestions):
            if not any(s != t and s in t for t in topic_suggestions):
                filtered.append(s)
        topic_suggestions = filtered

        linked_markdown = linkify_topics(markdown_content, topic_suggestions)
        html_content_final = convert_markdown(linked_markdown)
        html_content_final = remove_duplicate_header(html_content_final, topic)

        return render_template("topic.html", topic=topic.title(), content=html_content_final, last_update=last_update, topic_suggestions=topic_suggestions)
    except BadRequest as e:
        return str(e), 400


@app.route("/<topic>/<subtopic>", methods=["GET"])
def subtopic_page(topic, subtopic):
    try:
        topic = validate_topic_slug(topic.strip())
        subtopic = validate_topic_slug(subtopic.strip())
        topic_key = topic.lower()
        subtopic_key = subtopic.lower()
        
        topic_data = get_topic_data(topic_key)
        if topic_data and "subtopics" in topic_data and subtopic_key in topic_data["subtopics"]:
            sub_content = topic_data["subtopics"][subtopic_key]
        else:
            sub_content = "Subtopic content not available yet."
        
        return render_template(
            "topic.html", topic=topic.title(), subtopic=subtopic.title(), content=sub_content
        )
    except BadRequest as e:
        return str(e), 400


@app.route("/report", methods=["POST"])
@limiter.limit("5 per minute")
def report_issue():
    """
    Expected JSON payload:
    {
       "topic": "Python",
       "report_details": "The section on history is outdated.",
       "sources": ["https://source1.com", "https://source2.com"]
    }
    """
    try:
        data = request.get_json()
        validate_json_payload(data, ["topic", "report_details", "sources"])

        topic = validate_topic_slug(data["topic"])
        report_details = sanitize_text(data["report_details"])
        sources = sanitize_urls(data["sources"])

        if not topic_exists(topic):
            return jsonify({"reply": "0", "message": "Topic not found."}), 404

        # Log the contribution
        log_contribution(
            request.remote_addr,
            request.headers.get('X-User-ID', 'anonymous'),
            'report',
            topic,
            report_details
        )

        topic_data = get_topic_data(topic)
        current_content = topic_data["content"] if topic_data else ""
        reply_code, updated_content = process_user_feedback(
            topic, current_content, "report", report_details, sources
        )

        updated_content = convert_markdown(updated_content)
        if reply_code.strip() == "1":
            update_store_content(topic, updated_content.strip())

        return jsonify(
            {"reply": reply_code.strip(), "updated_content": updated_content.strip()}
        )
    except BadRequest as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logging.error(f"Error in report_issue: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500


@app.route("/add_info", methods=["POST"])
@limiter.limit("5 per minute")
def add_information():
    """
    Expected JSON payload:
    {
       "topic": "Python",
       "subtopic": "Libraries",
       "info": "Python has many libraries for data science...",
       "sources": ["https://example.com"]
    }
    """
    try:
        data = request.get_json()
        validate_json_payload(data, ["topic", "subtopic", "info", "sources"])

        topic = validate_topic_slug(data["topic"])
        subtopic = validate_topic_slug(data["subtopic"])
        info = sanitize_text(data["info"])
        sources = sanitize_urls(data["sources"])

        if not topic_exists(topic):
            return jsonify({"reply": "0", "message": "Topic not found."}), 404

        # Log the contribution
        log_contribution(
            request.remote_addr,
            request.headers.get('X-User-ID', 'anonymous'),
            'add_info',
            topic,
            f"Added info to subtopic: {subtopic}"
        )

        topic_data = get_topic_data(topic)
        current_content = topic_data["content"] if topic_data else ""
        reply_code, updated_content = process_user_feedback(
            topic, current_content, "add_info", info, sources
        )

        updated_content = convert_markdown(updated_content)
        if reply_code.strip() == "1":
            update_store_content(topic, updated_content.strip())
            # Optionally, update subtopics in the database if needed

        return jsonify(
            {"reply": reply_code.strip(), "updated_content": updated_content.strip()}
        )
    except BadRequest as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logging.error(f"Error in add_information: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500


if __name__ == "__main__":
    # Check command line arguments
    use_local_llm = len(sys.argv) > 1 and sys.argv[1] == "local"
    
    if use_local_llm:
        print("🔧 Starting in local LLM mode...")
        # Import local LLM validation
        from agents.local_llm import validate_local_llm_setup
        
        # Validate local LLM setup
        if not validate_local_llm_setup():
            print("❌ Local LLM setup validation failed. Exiting.")
            sys.exit(1)
        
        # Set the LLM mode to local
        set_llm_mode(True)
        print("✅ Local LLM mode activated")
    else:
        print("🌐 Starting in OpenAI API mode...")
        # Check if OpenAI API key is available
        if not os.environ.get("OPENAI_API_KEY"):
            print("⚠️  Warning: OPENAI_API_KEY environment variable not set.")
            print("   The application may not work properly without a valid API key.")
        set_llm_mode(False)
        print("✅ OpenAI API mode activated")
    
    print("🚀 Starting Flask application...")
    app.run(debug=True)
