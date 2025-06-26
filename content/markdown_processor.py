"""
Markdown Processor
Handles markdown to HTML conversion and content processing.
"""

import re
import markdown
import pymdownx.arithmatex
from security.validators import sanitize_html


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


def preprocess_math_blocks(content):
    """
    Convert [ ... ] blocks that look like LaTeX math to $$ ... $$ for MathJax rendering.
    Only replaces blocks that contain LaTeX commands (e.g., \begin, \sum, _{, ^{, etc.).
    """
    import re
    # Replace [ ... ] with $$ ... $$ if it looks like LaTeX math
    def replacer(match):
        inner = match.group(1)
        # Heuristic: if it contains LaTeX commands, treat as math
        if re.search(r'\\(begin|end|sum|frac|cdot|vdots|mathbb|[a-zA-Z]+_\{|[a-zA-Z]+\^\{)', inner):
            return f'$$\n{inner}\n$$'
        return match.group(0)
    # Only replace if [ ... ] is on its own line or surrounded by whitespace
    return re.sub(r'\[\s*([^\]]+?)\s*\]', replacer, content)


def convert_markdown(content):
    """
    Convert Markdown text to HTML using the 'extra' and 'toc' extensions.
    Then post-process the HTML to linkify reference markers and add IDs to reference list items.
    Finally, sanitize the HTML to prevent XSS attacks.
    """
    # Preprocess math blocks
    content = preprocess_math_blocks(content)
    html = markdown.markdown(
        content,
        extensions=["extra", "toc", "pymdownx.arithmatex"],
        extension_configs={
            "pymdownx.arithmatex": {"generic": True}
        }
    )
    html = linkify_references(html)
    html = add_reference_ids(html)
    html = sanitize_html(html)  # Sanitize HTML before returning
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


def linkify_topics(markdown_content, topic_suggestions):
    """
    Linkify suggested topics in markdown content.
    Prioritizes longer phrases over subwords.
    """
    import re
    # Sort by length descending to prioritize longer phrases
    suggestions = sorted(topic_suggestions, key=lambda x: -len(x))
    used = set()
    
    def replacer(match):
        phrase = match.group(0)
        if phrase in used:
            return phrase
        used.add(phrase)
        url = "/" + phrase.replace(" ", "%20")
        return f"[{phrase}]({url})"
    
    # Avoid linking inside existing markdown links
    for phrase in suggestions:
        # Regex: match phrase not inside []()
        pattern = r'(?<!\[)\b' + re.escape(phrase) + r'\b(?![^\[]*\])'
        markdown_content = re.sub(pattern, replacer, markdown_content, flags=re.IGNORECASE)
    
    return markdown_content 