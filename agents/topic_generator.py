"""
Topic Generation Agent
Handles LLM interactions for generating and updating encyclopedia articles.
"""

import os
from openai import OpenAI

# Initialize the OpenAI client
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))


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
        model="gpt-4.1",
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
        reply_code, markdown_content = text.split("\n", 1)
    except ValueError:
        reply_code, markdown_content = "0", text

    # Do NOT convert to HTML here; return markdown_content
    return reply_code, markdown_content


def update_topic_content(topic, current_content):
    """
    Use the LLM to check for updates to the topic, keeping the structure intact.
    """
    prompt = (
        f"The following is an encyclopedia article about '{topic}'. Please check if any information is outdated or missing as of today. "
        "If there are updates, rewrite the article with the same structure and section headers, only updating the content where necessary. "
        "If the article is already up to date, return it unchanged. Return your response starting with a reply code (1 for updated, 0 for unchanged) on the first line, followed by the article text.\n\n"
        f"{current_content}"
    )
    response = client.chat.completions.create(
        model="gpt-4.1",
        store=True,
        messages=[
            {"role": "system", "content": "You are a knowledgeable encyclopedia updater."},
            {"role": "user", "content": prompt},
        ],
        max_tokens=800,
        temperature=0.7,
    )
    text = response.choices[0].message.content.strip()
    try:
        reply_code, content = text.split("\n", 1)
    except ValueError:
        reply_code, content = "0", current_content
    return reply_code, content


def extract_topic_suggestions(article_text):
    """
    Use the LLM to extract a list of potential new article topics (words or phrases) from the article text.
    Returns a list of strings.
    """
    prompt = (
        "Analyze the following encyclopedia article and extract a list of words or phrases that would make good new article topics. "
        "Return only a Python list of strings, sorted by relevance, with longer phrases before their subwords if both are present. "
        "Do not include the main topic itself.\n\n"
        f"{article_text}"
    )
    response = client.chat.completions.create(
        model="gpt-4.1",
        store=True,
        messages=[
            {"role": "system", "content": "You are an assistant that extracts topic suggestions from encyclopedia articles."},
            {"role": "user", "content": prompt},
        ],
        max_tokens=300,
        temperature=0.3,
    )
    # Try to safely evaluate the list from the LLM response
    import ast
    text = response.choices[0].message.content.strip()
    try:
        suggestions = ast.literal_eval(text)
        if not isinstance(suggestions, list):
            suggestions = []
    except Exception:
        suggestions = []
    return suggestions


def process_user_feedback(topic, current_content, feedback_type, feedback_details, sources):
    """
    Process user feedback (reports or additions) using the LLM.
    """
    if feedback_type == "report":
        prompt = (
            f"The following encyclopedia article might contain errors:\n\n"
            f"{current_content}\n\n"
            f"A user reported the following issue: {feedback_details}\n"
            f"Sources: {', '.join(sources)}\n\n"
            "If the report is valid, update the article accordingly. "
            "Return your response starting with a reply code (1 for accepted, 0 for irrelevant) "
            "on the first line, followed by the updated article content."
        )
    elif feedback_type == "add_info":
        prompt = (
            f"For the article on '{topic}', the user suggests adding the following information: {feedback_details}\n\n"
            f"Sources: {', '.join(sources)}\n\n"
            "If this information is relevant and should be added, update the article accordingly. "
            "Return your response starting with a reply code (1 for accepted, 0 for irrelevant) on the first line, "
            "followed by the updated article text that includes this new information."
        )
    else:
        return "0", current_content

    response = client.chat.completions.create(
        model="gpt-4.1",
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

    return reply_code, updated_content 