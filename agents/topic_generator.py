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

# Initialize the OpenAI client lazily
client = None


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
    global USE_LOCAL_LLM, client
    
    if USE_LOCAL_LLM:
        local_client = get_local_llm_client()
        if local_client is None:
            logging.error("Local LLM client not available")
            return None
        
        model = get_local_llm_model()
        return local_client.generate(model, messages, max_tokens, temperature)
    else:
        # Initialize OpenAI client lazily
        if client is None:
            client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        
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
    global USE_LOCAL_LLM
    
    if USE_LOCAL_LLM:
        # Simplified prompt for local LLMs to avoid timeouts
        prompt = (
            f"Write a short encyclopedia article about '{topic}' in Markdown format. "
            "Include sections: Overview, History, Applications. "
            "Add a References section with 3-4 sources. "
            "Start with reply code 1 on first line, then the article."
        )
    else:
        # Full prompt for OpenAI API
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

    # Clean up reply code (handle variations like "Reply Code: 1")
    reply_code = reply_code.strip()
    if reply_code.lower().startswith("reply code:"):
        reply_code = reply_code.split(":", 1)[1].strip()
    elif reply_code.lower().startswith("reply code"):
        reply_code = reply_code.split(" ", 2)[2].strip()

    # Only validate references if not ambiguous
    if reply_code == "1":
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


def generate_topic_suggestions_from_text(selected_text, current_topic=""):
    """
    Generate topic suggestions based on selected text from an article.
    Returns a list of 3 relevant topic suggestions extracted from the selected text.
    """
    prompt = (
        f"EXTRACT ONLY terms that are ACTUALLY MENTIONED in the selected text below. "
        f"Do NOT generate related concepts or interpretations. "
        f"Look for specific words, phrases, or terms that appear in the text and could be encyclopedia topics.\n\n"
        f"Selected text: '{selected_text}'\n\n"
        f"Current article topic: {current_topic}\n\n"
        f"CRITICAL RULES:\n"
        f"1. ONLY extract terms that are EXPLICITLY mentioned in the selected text\n"
        f"2. Do NOT generate related concepts, synonyms, or broader categories\n"
        f"3. Do NOT interpret or expand on the text\n"
        f"4. If the text says 'programming language', extract 'programming language' (not 'computer programming')\n"
        f"5. If the text mentions specific names, extract those names\n"
        f"6. If the text mentions specific concepts, extract those exact concepts\n"
        f"7. If fewer than 3 terms are found, repeat some terms or use 'No additional terms found'\n\n"
        f"Examples:\n"
        f"- Text: 'Python is a programming language' → Extract: ['Python', 'programming language']\n"
        f"- Text: 'machine learning algorithms' → Extract: ['machine learning', 'algorithms']\n"
        f"- Text: 'web development frameworks' → Extract: ['web development', 'frameworks']\n"
        f"- Text: 'programming language' → Extract: ['programming language'] (not 'computer programming')\n\n"
        f"Return exactly 3 terms in this format: ['Term 1', 'Term 2', 'Term 3']"
    )
    
    text = _call_llm([
        {"role": "system", "content": "You are an assistant that extracts ONLY terms explicitly mentioned in text. Do NOT generate related concepts or interpretations."},
        {"role": "user", "content": prompt},
    ], max_tokens=200, temperature=0.1)
    
    if text is None:
        return extract_terms_fallback(selected_text)
    
    # Try to safely evaluate the list from the LLM response
    import ast
    try:
        suggestions = ast.literal_eval(text)
        if isinstance(suggestions, list) and len(suggestions) >= 3:
            # Validate that suggestions are actually from the text
            validated_suggestions = validate_suggestions_against_text(suggestions, selected_text)
            return validated_suggestions[:3]
        else:
            return extract_terms_fallback(selected_text)
    except Exception:
        return extract_terms_fallback(selected_text)


def extract_terms_fallback(selected_text):
    """
    Fallback method to extract terms from selected text using simple text analysis.
    """
    import re
    
    # Clean the text
    text = selected_text.lower().strip()
    
    # Common programming/tech terms to look for
    programming_terms = [
        'programming', 'language', 'programming language', 'python', 'javascript', 'java', 'c++', 'c#', 'php',
        'html', 'css', 'sql', 'database', 'algorithm', 'data structure', 'framework', 'library',
        'api', 'web development', 'frontend', 'backend', 'full stack', 'mobile development',
        'machine learning', 'artificial intelligence', 'ai', 'ml', 'deep learning', 'neural network',
        'cloud computing', 'aws', 'azure', 'google cloud', 'docker', 'kubernetes', 'git',
        'agile', 'scrum', 'devops', 'testing', 'unit test', 'integration test'
    ]
    
    # Find terms that appear in the text
    found_terms = []
    for term in programming_terms:
        if term in text:
            found_terms.append(term)
    
    # If we found terms, return them
    if found_terms:
        # Ensure we have exactly 3 terms
        while len(found_terms) < 3:
            found_terms.append(found_terms[0] if found_terms else "programming")
        return found_terms[:3]
    
    # If no programming terms found, extract noun phrases
    words = re.findall(r'\b\w+\b', text)
    if len(words) >= 3:
        return words[:3]
    elif len(words) > 0:
        return words + [words[0]] * (3 - len(words))
    else:
        return ["No terms found", "Please try selecting different text", "Or enter your own topic"]


def validate_suggestions_against_text(suggestions, selected_text):
    """
    Validate that suggestions are actually present in the selected text.
    """
    text_lower = selected_text.lower()
    validated = []
    
    for suggestion in suggestions:
        if suggestion.lower() in text_lower:
            validated.append(suggestion)
        else:
            # If suggestion is not in text, try to find a similar term
            words = suggestion.lower().split()
            for word in words:
                if word in text_lower and len(word) > 2:  # Only meaningful words
                    validated.append(word)
                    break
            else:
                # If no match found, use the original but mark it
                validated.append(suggestion)
    
    # Ensure we have exactly 3 suggestions
    while len(validated) < 3:
        validated.append("No additional terms found")
    
    return validated[:3]


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


def validate_topic_name_with_llm(topic_name):
    """
    Use the LLM to check if the input is a valid encyclopedia article name.
    If not, return a list of suggested valid names from the input.
    Returns (is_valid, suggestions_or_reason).
    """
    prompt = (
        f"You are an expert encyclopedia editor. A user entered the following as a potential article name: '{topic_name}'.\n"
        "Determine if this is a valid, specific, and appropriate encyclopedia article name (not too vague, not a sentence, not a question, not a list, not a random string, not too short, not too long, not just numbers or symbols, not offensive, etc).\n"
        "If it is a valid article name, reply with 'VALID' on the first line.\n"
        "If it is NOT a valid article name, reply with 'INVALID' on the first line, then a short reason, then a list of up to 5 suggested valid article names that could be extracted from the input (if any).\n"
        f"\nInput: {topic_name}\n"
        "Reply format:\nVALID\n--or--\nINVALID\n<reason>\n- suggestion 1\n- suggestion 2\n...\n"
    )
    text = _call_llm([
        {"role": "system", "content": "You are an expert encyclopedia editor."},
        {"role": "user", "content": prompt},
    ], max_tokens=200, temperature=0.2)
    if text is None:
        return False, ["Error: Unable to validate topic name."]
    lines = text.strip().splitlines()
    if not lines:
        return False, ["Error: No response from LLM."]
    if lines[0].strip().upper() == 'VALID':
        return True, None
    elif lines[0].strip().upper() == 'INVALID':
        reason = lines[1] if len(lines) > 1 else "Not a valid article name."
        suggestions = [l.lstrip('-').strip() for l in lines[2:] if l.strip().startswith('-') or l.strip()]
        return False, (reason, suggestions)
    else:
        return False, ["Unrecognized response from LLM:", text] 