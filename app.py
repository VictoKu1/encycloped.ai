import os
from flask import Flask, render_template, request, redirect, url_for, jsonify
import openai  # Make sure you have installed openai (`pip install openai`)

# Initialize Flask app
app = Flask(__name__)

# Configure your OpenAI API key
openai.api_key = os.environ.get("OPENAI_API_KEY")

# A simple in-memory datastore for demo purposes
# In production, consider using a proper database.
data_store = {}  # e.g., {'Python': {'content': '...', 'subtopics': {...}}}


def generate_topic_content(topic):
    """Call ChatGPT API to generate encyclopedia-style content with citations."""
    prompt = (
        f"Write an encyclopedia-style article about '{topic}'. "
        "Include citations for every piece of information. "
        "Return the answer starting with a reply code (1 for accepted) "
        "on the first line, followed by the article text."
    )

    response = openai.Completion.create(
        engine="text-davinci-003", prompt=prompt, max_tokens=800, temperature=0.7
    )

    text = response.choices[0].text.strip()
    # Expecting response like:
    # 1
    # Article content...
    try:
        reply_code, content = text.split("\n", 1)
    except ValueError:
        reply_code, content = "0", text  # default in case formatting is off

    return reply_code, content


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        topic = request.form.get("topic", "").strip()
        if topic:
            # Redirect to the topic page
            return redirect(url_for("topic_page", topic=topic))
    return render_template("index.html")


@app.route("/<topic>", methods=["GET"])
def topic_page(topic):
    topic = topic.strip()
    if topic in data_store:
        content = data_store[topic]["content"]
    else:
        # Optionally, you could start a background process for generation.
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

    # Retrieve current content
    if topic not in data_store:
        return jsonify({"reply": "0", "message": "Topic not found."}), 404
    current_content = data_store[topic]["content"]

    # Create a prompt to ask ChatGPT to validate and fix the content.
    prompt = (
        f"The following encyclopedia article might contain errors:\n\n"
        f"{current_content}\n\n"
        f"A user reported the following issue: {report_details}\n"
        f"Sources: {', '.join(sources)}\n\n"
        "If the report is valid, update the article accordingly. "
        "Return your response starting with a reply code (1 for accepted, 0 for irrelevant) "
        "on the first line, followed by the updated article content."
    )

    response = openai.Completion.create(
        engine="text-davinci-003", prompt=prompt, max_tokens=800, temperature=0.7
    )

    text = response.choices[0].text.strip()
    try:
        reply_code, updated_content = text.split("\n", 1)
    except ValueError:
        reply_code, updated_content = "0", current_content

    if reply_code.strip() == "1":
        # Update the datastore
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

    # Build a prompt to validate the addition.
    prompt = (
        f"For the article on '{topic}', the user suggests adding the following information under the subtopic '{subtopic}':\n\n"
        f"{info}\n\n"
        f"Sources: {', '.join(sources)}\n\n"
        "If this information is relevant and should be added, update the article accordingly. "
        "Return your response starting with a reply code (1 for accepted, 0 for irrelevant) on the first line, "
        "followed by the updated article text that includes this new subtopic section."
    )

    response = openai.Completion.create(
        engine="text-davinci-003", prompt=prompt, max_tokens=800, temperature=0.7
    )

    text = response.choices[0].text.strip()
    try:
        reply_code, updated_content = text.split("\n", 1)
    except ValueError:
        reply_code, updated_content = "0", data_store[topic]["content"]

    if reply_code.strip() == "1":
        # Update the main article content or add as a subtopic.
        data_store[topic]["content"] = updated_content.strip()
        # Optionally, also update the subtopics dictionary.
        data_store[topic]["subtopics"][
            subtopic
        ] = info.strip()  # or some processed version
    return jsonify(
        {"reply": reply_code.strip(), "updated_content": updated_content.strip()}
    )


if __name__ == "__main__":
    app.run(debug=True)
