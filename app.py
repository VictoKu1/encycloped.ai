import os
import re
import markdown
from flask import Flask, render_template, request, redirect, url_for, jsonify
from openai import OpenAI

# Initialize the OpenAI client; ensure your OPENAI_API_KEY is set in your environment
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# Initialize Flask app
app = Flask(__name__)

# A simple in-memory datastore for demo purposes.
data_store = {}  # e.g., {'Python': {'content': '...', 'subtopics': {...}}}

# --- Markdown Processing Helpers ---


def linkify_references(html):
    """
    Replace in-text reference markers like [1] with clickable links pointing to the reference section.
    """

    def repl(match):
        num = match.group(1)
        return f'<a href="#ref{num}">[{num}]</a>'

    return re.sub(r"\[(\d+)\]", repl, html)


def add_reference_ids(html):
    """
    Add id attributes to reference list items so that clickable links work.
    This function looks for list items whose first element is an anchor linking to "#refX"
    and adds the id attribute to the <li> element.
    """
    html = re.sub(
        r'(<li>)(\s*<a href="#ref(\d+)">\[?\3\]?</a>)', r'<li id="ref\3">\2', html
    )
    return html


def convert_markdown(content):
    """
    Convert Markdown text to HTML using the 'extra' and 'toc' extensions.
    Then post-process the HTML to linkify reference markers and add IDs to reference list items.
    """
    html = markdown.markdown(content, extensions=["extra", "toc"])
    html = linkify_references(html)
    html = add_reference_ids(html)
    return html


def remove_duplicate_header(html, topic):
    """
    If the first header in the HTML is a <h1> that contains the topic (or a close variant),
    remove that header so that it doesn't duplicate the main page header.
    """
    # Define a regex to match a leading <h1> tag.
    pattern = r"^\s*<h1[^>]*>.*?</h1>\s*"
    # Check if the first header seems to contain the topic (case-insensitive)
    match = re.search(pattern, html, flags=re.IGNORECASE)
    if match:
        header_text = re.sub(
            r"<[^>]+>", "", match.group(0)
        )  # remove tags to get just the text
        if topic.lower() in header_text.lower():
            # Remove the header from the HTML
            html = re.sub(pattern, "", html, count=1, flags=re.IGNORECASE)
    return html


# --- End Markdown Processing Helpers ---


def generate_topic_content(topic):
    """
    Call the OpenAI Chat API to generate an encyclopedia-style article with Markdown formatting.
    The article will include clear section headers and a separate References section.
    """
    prompt = (
        f"Write an encyclopedia-style article about '{topic}' using Markdown formatting. "
        "Divide the article into clear sections with headers such as 'TL;DR' 'Overview', 'History', "
        "'Features and Syntax', 'Applications', and 'Community and Development'. "
        "At the end, include a 'References' section. In that section, list each reference on a separate line as a Markdown list item (each line should start with '- '). "
        "Within the article text, in-text reference markers like [1] should be clickable links that jump to the corresponding reference. "
        "Return the answer starting with a reply code (1 for accepted) on the first line, followed by the article text."
    )

    response = client.chat.completions.create(
        model="gpt-4o",  # Adjust if needed
        store=True,
        messages=[
            {
                "role": "system",
                "content": "You are a knowledgeable encyclopedia writer.",
            },
            {"role": "user", "content": prompt},
        ],
        max_tokens=800,
        temperature=0.7,
    )

    text = response.choices[0].message.content.strip()
    try:
        reply_code, content = text.split("\n", 1)
    except ValueError:
        reply_code, content = "0", text

    # Convert the Markdown content to HTML
    content = convert_markdown(content)
    # Remove duplicate header if it repeats the topic
    content = remove_duplicate_header(content, topic)
    return reply_code, content


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        topic = request.form.get("topic", "").strip()
        if topic:
            return redirect(url_for("topic_page", topic=topic))
    return render_template("index.html")


@app.route("/<topic>", methods=["GET"])
def topic_page(topic):
    topic = topic.strip()
    if topic in data_store:
        content = data_store[topic]["content"]
    else:
        reply_code, content = generate_topic_content(topic)
        data_store[topic] = {"content": content, "subtopics": {}}
    return render_template("topic.html", topic=topic, content=content)


@app.route("/<topic>/<subtopic>", methods=["GET"])
def subtopic_page(topic, subtopic):
    topic = topic.strip()
    subtopic = subtopic.strip()
    if topic in data_store and subtopic in data_store[topic]["subtopics"]:
        sub_content = data_store[topic]["subtopics"][subtopic]
    else:
        sub_content = "Subtopic content not available yet."
    return render_template(
        "topic.html", topic=topic, subtopic=subtopic, content=sub_content
    )


@app.route("/report", methods=["POST"])
def report_issue():
    """
    Expected JSON payload:
    {
       "topic": "Python",
       "report_details": "The section on history is outdated.",
       "sources": ["https://source1.com", "https://source2.com"]
    }
    """
    data = request.get_json()
    topic = data.get("topic")
    report_details = data.get("report_details")
    sources = data.get("sources")

    if topic not in data_store:
        return jsonify({"reply": "0", "message": "Topic not found."}), 404
    current_content = data_store[topic]["content"]

    prompt = (
        f"The following encyclopedia article might contain errors:\n\n"
        f"{current_content}\n\n"
        f"A user reported the following issue: {report_details}\n"
        f"Sources: {', '.join(sources)}\n\n"
        "If the report is valid, update the article accordingly. "
        "Return your response starting with a reply code (1 for accepted, 0 for irrelevant) "
        "on the first line, followed by the updated article content."
    )

    response = client.chat.completions.create(
        model="gpt-4o",
        store=True,
        messages=[
            {
                "role": "system",
                "content": "You are a helpful assistant for editing encyclopedia articles.",
            },
            {"role": "user", "content": prompt},
        ],
        max_tokens=800,
        temperature=0.7,
    )

    text = response.choices[0].message.content.strip()
    try:
        reply_code, updated_content = text.split("\n", 1)
    except ValueError:
        reply_code, updated_content = "0", current_content

    updated_content = convert_markdown(updated_content)
    if reply_code.strip() == "1":
        data_store[topic]["content"] = updated_content.strip()

    return jsonify(
        {"reply": reply_code.strip(), "updated_content": updated_content.strip()}
    )


@app.route("/add_info", methods=["POST"])
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
    data = request.get_json()
    topic = data.get("topic")
    subtopic = data.get("subtopic")
    info = data.get("info")
    sources = data.get("sources")

    if topic not in data_store:
        return jsonify({"reply": "0", "message": "Topic not found."}), 404

    prompt = (
        f"For the article on '{topic}', the user suggests adding the following information under the subtopic '{subtopic}':\n\n"
        f"{info}\n\n"
        f"Sources: {', '.join(sources)}\n\n"
        "If this information is relevant and should be added, update the article accordingly. "
        "Return your response starting with a reply code (1 for accepted, 0 for irrelevant) on the first line, "
        "followed by the updated article text that includes this new subtopic section."
    )

    response = client.chat.completions.create(
        model="gpt-4o",
        store=True,
        messages=[
            {
                "role": "system",
                "content": "You are a helpful assistant for editing encyclopedia articles.",
            },
            {"role": "user", "content": prompt},
        ],
        max_tokens=800,
        temperature=0.7,
    )

    text = response.choices[0].message.content.strip()
    try:
        reply_code, updated_content = text.split("\n", 1)
    except ValueError:
        reply_code, updated_content = "0", data_store[topic]["content"]

    updated_content = convert_markdown(updated_content)
    if reply_code.strip() == "1":
        data_store[topic]["content"] = updated_content.strip()
        # Convert the added subtopic info to HTML as well.
        data_store[topic]["subtopics"][subtopic] = convert_markdown(info.strip())

    return jsonify(
        {"reply": reply_code.strip(), "updated_content": updated_content.strip()}
    )


if __name__ == "__main__":
    app.run(debug=True)
