"""
Topic Generation Agent
Handles LLM interactions for generating and updating encyclopedia articles.
Supports both OpenAI API and local LLM via Ollama.
"""

import os
from openai import OpenAI
import logging
from typing import Optional

# Import local LLM functionality
from .local_llm import get_local_llm_client, get_local_llm_model

# Global flag to determine which LLM to use
USE_LOCAL_LLM = False

# Initialize the OpenAI client
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))


def set_llm_mode(use_local: bool):
    """Set whether to use local LLM or OpenAI API."""
    global USE_LOCAL_LLM
    USE_LOCAL_LLM = use_local
    if use_local:
        logging.info("Using local LLM mode")
    else:
        logging.info("Using OpenAI API mode")


def _call_llm(messages: list, max_tokens: int = 800, temperature: float = 0.7) -> Optional[str]:
    """Unified interface to call either OpenAI or local LLM."""
    global USE_LOCAL_LLM
    
    if USE_LOCAL_LLM:
        local_client = get_local_llm_client()
        if local_client is None:
            logging.error("Local LLM client not available")
            return None
        
        model = get_local_llm_model()
        return local_client.generate(model, messages, max_tokens, temperature)
    else:
        try:
            response = client.chat.completions.create(
                model="gpt-4.1",
                store=True,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logging.error(f"OpenAI API error: {e}")
            return None


def generate_topic_content(topic):
    """
    Call the OpenAI Chat API to generate an encyclopedia-style article with Markdown formatting.
    If the topic is ambiguous (has multiple common meanings), do NOT generate an article. Instead, return a short intro sentence (e.g., 'The topic <topic> may have several meanings, did you mean:'), then a numbered list (one per line, e.g., '1. topic (option1)'), and return the special code 45 as the reply code. If the topic is unambiguous, generate the article as before.
    """
    prompt = (
        f"Write an encyclopedia-style article about '{topic}' using Markdown formatting, UNLESS the topic is ambiguous (has multiple common meanings or interpretations). "
        "If the topic is ambiguous, do NOT generate an article. Instead, return a short intro sentence (for example: 'The topic <topic> may have several meanings, did you mean:'), then a numbered list, one per line, where each line is in the format '1. topic (option1)', '2. topic (option2)', etc. Do not add any extra explanations or formatting. Return the special code 45 as the reply code on the first line. For example, if the topic is 'Mercury', you might return: \n45\nThe topic Mercury may have several meanings, did you mean:\n1. Mercury (planet)\n2. Mercury (element)\n3. Mercury (mythology)\n (but do NOT use this example in your output). "
        "If the topic is unambiguous, divide the article into clear sections with headers such as 'TL;DR', 'Overview', 'History', 'Features and Syntax', 'Applications', and 'Community and Development'. "
        "At the end, include a 'References' section. In that section, list minimum 4-5 references (but as many as are appropriate for the topic), each on a separate line as a Markdown list item (each line should start with '- '). "
        "Each reference must include a title and a URL (e.g., '- [1]: Example Source <https://example.com>'). "
        "NOTE: The sources should be valid and real, not just placeholders. Source with a URL https://example.com is not a valid source, its just an example and should not be used in any article as a source). "
        "Within the article text, in-text reference markers like [1] should be clickable links that jump to the corresponding reference. "
        "Every in-text reference (e.g., [1]) must have a corresponding entry in the References section, and every reference in the list must be cited in the text. "
        "If you cannot find real references, use reputable placeholder titles and URLs. "
        "Return the answer starting with a reply code (1 for accepted, 45 for ambiguous, 0 for error) on the first line, followed by the article text or the list of meanings."
    )

    text = _call_llm([
        {
            "role": "system",
            "content": "You are a knowledgeable encyclopedia writer.",
        },
        {"role": "user", "content": prompt},
    ])
    
    if text is None:
        return "0", "Error: Unable to generate content"
    logging.info(f"[OPENAI RAW GENERATION] Topic: {topic}\n{text}")
    try:
        reply_code, markdown_content = text.split("\n", 1)
    except ValueError:
        reply_code, markdown_content = "0", text

    # Only validate references if not ambiguous
    if reply_code.strip() == "1":
        markdown_content = validate_references(markdown_content)
    return reply_code, markdown_content


def validate_references(markdown_content):
    """
    Ensure the References section exists, is non-empty, and all in-text citations match the list.
    Only include references with a plausible URL. If no valid references, remove the References section entirely.
    """
    import re
    lines = markdown_content.splitlines()
    # Find the References section
    ref_start = None
    for i, line in enumerate(lines):
        if line.strip().lower().startswith('## references') or line.strip().lower().startswith('# references'):
            ref_start = i
            break
    if ref_start is None:
        # No references section, nothing to validate
        return '\n'.join(lines)
    # Collect all in-text citations [n]
    intext_refs = set(re.findall(r'\[(\d+)\]', '\n'.join(lines[:ref_start])))
    # Collect all reference list items after the References header
    ref_lines = lines[ref_start+1:]
    ref_items = [re.match(r'- \[?(\d+)\]?[:：]?(.*)', l.strip()) for l in ref_lines if l.strip().startswith('-')]
    ref_nums = set(m.group(1) for m in ref_items if m)
    # Only keep references that have a plausible URL
    valid_refs = []
    for m in ref_items:
        if not m:
            continue
        num, rest = m.group(1), m.group(2).strip()
        # Check for plausible URL in <...>
        url_match = re.search(r'<(https?://[^>]+)>', rest)
        if rest and url_match:
            valid_refs.append((num, rest))
    # Only keep references that are cited in-text
    valid_refs = [r for r in valid_refs if r[0] in intext_refs]
    # If no valid references, remove the References section
    if not valid_refs:
        return '\n'.join(lines[:ref_start])
    # Otherwise, reconstruct the References section
    fixed_lines = lines[:ref_start+1]
    for num, rest in valid_refs:
        fixed_lines.append(f'- [{num}]: {rest}')
    # Add any non-list lines after references
    for l in ref_lines:
        if not l.strip().startswith('-'):
            fixed_lines.append(l)
    return '\n'.join(fixed_lines)


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
    text = _call_llm([
        {"role": "system", "content": "You are a knowledgeable encyclopedia updater."},
        {"role": "user", "content": prompt},
    ])
    
    if text is None:
        return "0", current_content
    logging.info(f"[OPENAI RAW UPDATE] Topic: {topic}\n{text}")
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
    text = _call_llm([
        {"role": "system", "content": "You are an assistant that extracts topic suggestions from encyclopedia articles."},
        {"role": "user", "content": prompt},
    ], max_tokens=300, temperature=0.3)
    
    if text is None:
        return []
    
    # Try to safely evaluate the list from the LLM response
    import ast
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

    text = _call_llm([
        {
            "role": "system",
            "content": "You are a helpful assistant for editing encyclopedia articles.",
        },
        {"role": "user", "content": prompt},
    ])
    
    if text is None:
        return "0", current_content
    try:
        reply_code, updated_content = text.split("\n", 1)
    except ValueError:
        reply_code, updated_content = "0", current_content

    return reply_code, updated_content 