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
    set_llm_mode,
    generate_topic_suggestions_from_text
)
from security.validators import (
    validate_topic_slug, 
    sanitize_text, 
    sanitize_urls, 
    log_contribution,
    validate_json_payload
)
from security.prompt_injection_detector import (
    validate_user_feedback,
    sanitize_for_llm_input
)
from security.review_queue import get_review_queue
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
    from flask import request
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    if request.method == "POST":
        topic = request.form.get("topic", "").strip()
        if topic:
            from agents.topic_generator import validate_topic_name_with_llm
            from utils.data_store import topic_exists
            if topic_exists(topic.lower()):
                try:
                    topic = validate_topic_slug(topic)
                    if is_ajax:
                        return jsonify({'redirect': url_for("topic_page", topic=topic)})
                    return redirect(url_for("topic_page", topic=topic))
                except BadRequest as e:
                    if is_ajax:
                        return {"reason": str(e), "suggestions": []}, 400
                    return str(e), 400
            if len(topic) > 255:
                if is_ajax:
                    return {"reason": "The topic name is too long (max 255 characters).", "suggestions": []}, 400
                return render_template("invalid_topic.html", reason="The topic name is too long (max 255 characters).", suggestions=[])
            is_valid, result = validate_topic_name_with_llm(topic)
            if is_valid:
                try:
                    topic = validate_topic_slug(topic)
                    if is_ajax:
                        return jsonify({'redirect': url_for("topic_page", topic=topic)})
                    return redirect(url_for("topic_page", topic=topic))
                except BadRequest as e:
                    if is_ajax:
                        return {"reason": str(e), "suggestions": []}, 400
                    return str(e), 400
            else:
                if isinstance(result, tuple):
                    reason, suggestions = result
                else:
                    reason, suggestions = result[0], result[1:] if isinstance(result, list) else []
                if is_ajax:
                    return {"reason": reason, "suggestions": suggestions}, 400
                return render_template("invalid_topic.html", reason=reason, suggestions=suggestions)
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
        report_details_raw = data["report_details"]
        sources_raw = data["sources"]
        
        # Validate user feedback for prompt injection before processing
        is_valid, error_msg = validate_user_feedback(report_details_raw, sources_raw)
        if not is_valid:
            logging.warning(f"Rejected report for topic '{topic}': {error_msg}")
            return jsonify({"error": error_msg}), 400
        
        # Sanitize inputs after validation
        report_details = sanitize_for_llm_input(sanitize_text(report_details_raw))
        sources = sanitize_urls(sources_raw)

        if not topic_exists(topic):
            return jsonify({"reply": "0", "message": "Topic not found."}), 404

        # Add submission to review queue for tracking and abuse detection
        review_queue = get_review_queue()
        submission = review_queue.add_submission(
            ip_address=request.remote_addr,
            user_id=request.headers.get('X-User-ID', 'anonymous'),
            action='report',
            topic=topic,
            content=report_details,
            sources=sources,
            auto_approve=True  # Auto-approve for now, can be changed to False for stricter control
        )

        # Log the contribution
        log_contribution(
            request.remote_addr,
            request.headers.get('X-User-ID', 'anonymous'),
            'report',
            topic,
            report_details[:100]  # Log only first 100 chars
        )
        
        # Check if submission should be queued for review
        if review_queue.should_require_review(submission):
            logging.info(
                f"Submission {submission['id']} flagged for review: {submission['flags']}"
            )
            return jsonify({
                "reply": "queued",
                "message": "Your submission has been queued for review due to automated safety checks.",
                "submission_id": submission['id']
            }), 202

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
        info_raw = data["info"]
        sources_raw = data["sources"]
        
        # Validate user feedback for prompt injection before processing
        is_valid, error_msg = validate_user_feedback(info_raw, sources_raw)
        if not is_valid:
            logging.warning(f"Rejected add_info for topic '{topic}': {error_msg}")
            return jsonify({"error": error_msg}), 400
        
        # Sanitize inputs after validation
        info = sanitize_for_llm_input(sanitize_text(info_raw))
        sources = sanitize_urls(sources_raw)

        if not topic_exists(topic):
            return jsonify({"reply": "0", "message": "Topic not found."}), 404

        # Add submission to review queue for tracking and abuse detection
        review_queue = get_review_queue()
        submission = review_queue.add_submission(
            ip_address=request.remote_addr,
            user_id=request.headers.get('X-User-ID', 'anonymous'),
            action='add_info',
            topic=topic,
            content=info,
            sources=sources,
            auto_approve=True  # Auto-approve for now, can be changed to False for stricter control
        )

        # Log the contribution
        log_contribution(
            request.remote_addr,
            request.headers.get('X-User-ID', 'anonymous'),
            'add_info',
            topic,
            f"Added info to subtopic: {subtopic}"
        )
        
        # Check if submission should be queued for review
        if review_queue.should_require_review(submission):
            logging.info(
                f"Submission {submission['id']} flagged for review: {submission['flags']}"
            )
            return jsonify({
                "reply": "queued",
                "message": "Your submission has been queued for review due to automated safety checks.",
                "submission_id": submission['id']
            }), 202

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


@app.route("/suggest_topics", methods=["POST"])
@limiter.limit("10 per minute")
def suggest_topics():
    """
    Generate topic suggestions based on selected text.
    Expected JSON payload:
    {
       "selected_text": "Python is a programming language...",
       "current_topic": "Python"
    }
    """
    try:
        data = request.get_json()
        validate_json_payload(data, ["selected_text"])
        
        selected_text = sanitize_text(data["selected_text"])
        current_topic = data.get("current_topic", "")
        
        if len(selected_text.strip()) < 10:
            return jsonify({"error": "Selected text is too short. Please select more text."}), 400
        
        # Generate topic suggestions using the LLM
        suggestions = generate_topic_suggestions_from_text(selected_text, current_topic)
        
        return jsonify({"suggestions": suggestions})
    except BadRequest as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logging.error(f"Error in suggest_topics: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500


@app.route("/add_reference", methods=["POST"])
def add_reference():
    """
    Add a new reference (hyperlink) to the article's markdown and persist it.
    Expected JSON payload:
    {
        "article_topic": "Python",
        "selected_text": "interpreted programming language",
        "reference_topic": "Programming Language"
    }
    """
    try:
        data = request.get_json()
        validate_json_payload(data, ["article_topic", "selected_text", "reference_topic"])
        article_topic = validate_topic_slug(data["article_topic"])
        selected_text = sanitize_text(data["selected_text"])
        reference_topic = sanitize_text(data["reference_topic"])
        topic_key = article_topic.lower()
        topic_data = get_topic_data(topic_key)
        if not topic_data:
            return jsonify({"error": "Topic not found."}), 404
        markdown_content = topic_data.get("markdown", "")
        topic_suggestions = topic_data.get("topic_suggestions", [])
        # Add the new reference topic to topic_suggestions if not present
        if reference_topic not in topic_suggestions:
            topic_suggestions.append(reference_topic)
        # Replace the first occurrence of selected_text with a markdown link
        import re
        def replace_first(text, sub, repl):
            pattern = re.escape(sub)
            return re.sub(pattern, repl, text, count=1)
        link_md = f"[{selected_text}](/" + reference_topic.replace(" ", "%20") + ")"
        new_markdown = replace_first(markdown_content, selected_text, link_md)
        # Save the updated markdown and topic suggestions
        from content.markdown_processor import linkify_topics, convert_markdown, remove_duplicate_header
        linked_markdown = linkify_topics(new_markdown, topic_suggestions)
        html_content_final = convert_markdown(linked_markdown)
        html_content_final = remove_duplicate_header(html_content_final, article_topic)
        save_topic_data(topic_key, html_content_final, new_markdown, topic_suggestions)
        return jsonify({"updated_content": html_content_final})
    except BadRequest as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        import traceback
        logging.error(f"Error in add_reference: {str(e)}\n{traceback.format_exc()}")
        return jsonify({"error": "Internal server error"}), 500


@app.route("/admin/review_queue", methods=["GET"])
def admin_review_queue():
    """
    Admin endpoint to view pending submissions in the review queue.
    This endpoint is for future implementation of human approval workflow.
    
    TODO: Add authentication/authorization before deploying to production.
    """
    try:
        review_queue = get_review_queue()
        
        # Get pending submissions
        pending = review_queue.get_pending_submissions()
        
        # Get statistics
        stats = review_queue.get_submission_stats()
        
        return jsonify({
            "statistics": stats,
            "pending_submissions": pending
        })
    except Exception as e:
        logging.error(f"Error in admin_review_queue: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500


@app.route("/admin/review_action", methods=["POST"])
def admin_review_action():
    """
    Admin endpoint to approve or reject a submission.
    
    Expected JSON payload:
    {
        "submission_id": "abc123",
        "action": "approve" or "reject",
        "reason": "optional rejection reason"
    }
    
    TODO: Add authentication/authorization before deploying to production.
    """
    try:
        data = request.get_json()
        validate_json_payload(data, ["submission_id", "action"])
        
        submission_id = data["submission_id"]
        action = data["action"]
        
        review_queue = get_review_queue()
        
        if action == "approve":
            success = review_queue.approve_submission(submission_id)
            if success:
                return jsonify({"status": "approved", "submission_id": submission_id})
            else:
                return jsonify({"error": "Submission not found"}), 404
                
        elif action == "reject":
            reason = data.get("reason", "")
            success = review_queue.reject_submission(submission_id, reason)
            if success:
                return jsonify({"status": "rejected", "submission_id": submission_id})
            else:
                return jsonify({"error": "Submission not found"}), 404
        else:
            return jsonify({"error": "Invalid action. Use 'approve' or 'reject'"}), 400
            
    except BadRequest as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logging.error(f"Error in admin_review_action: {str(e)}")
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
    app.run(debug=True, use_reloader=False)
