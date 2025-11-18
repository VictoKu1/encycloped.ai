"""
Prompt Injection Detection
Implements heuristic-based detection of potential prompt injection attacks in user input.
"""

import re
import logging


# Patterns that might indicate prompt injection attempts
SUSPICIOUS_PATTERNS = [
    # Direct instruction patterns - more flexible ordering
    r"(?i)ignore\s+(all\s+)?(previous|prior|above)\s+(instructions?|prompts?|rules?|commands?)",
    r"(?i)ignore\s+(previous|all|above|prior)\s+(instructions?|prompts?|rules?|commands?)",
    r"(?i)(disregard|forget|override)\s+(previous|all|above|prior)\s+(instructions?|prompts?|rules?|commands?)",
    r"(?i)^(you\s+are|you're|act\s+as|pretend\s+to\s+be|roleplay|imagine\s+you\s+are)",
    r"(?i)(new\s+instructions?|updated\s+instructions?|system\s+prompt)",
    r"(?i)(do\s+not|don't|never)\s+(follow|obey|listen\s+to)\s+(instructions?|rules?|guidelines?)",
    
    # Role manipulation
    r"(?i)(instead|rather|now),?\s+(you\s+are|you're|act\s+as|become)",
    r"(?i)(from\s+now\s+on|starting\s+now|beginning\s+now)",
    
    # System-level commands
    r"(?i)(system|admin|root|sudo)\s*(:|mode|prompt|command)",
    r"(?i)(execute|run|eval|evaluate)\s+(command|code|script)",
    
    # Output manipulation
    r"(?i)(output|print|return|display|show)\s+(only|just|exactly)",
    r"(?i)(respond\s+with|reply\s+with|say\s+only)\s+['\"]",
    
    # Context escaping
    r"(?i)(end\s+of|exit|escape|break\s+out\s+of)\s+(context|role|character|mode)",
    r"(?i)```\s*python|```\s*javascript|```\s*bash",  # Code blocks might be used for injection
    
    # Data exfiltration attempts
    r"(?i)(show|reveal|display|print)\s+(your|the)\s+(prompt|instructions?|system|rules?)",
]


def detect_prompt_injection(user_input: str, threshold: float = 0.5) -> tuple[bool, float, list]:
    """
    Detect potential prompt injection attempts in user input.
    
    Args:
        user_input: The user-provided text to analyze
        threshold: Suspicion threshold (0.0 to 1.0) - lower is more strict
        
    Returns:
        tuple: (is_suspicious, suspicion_score, matched_patterns)
            - is_suspicious: True if input appears to be a prompt injection attempt
            - suspicion_score: 0.0 to 1.0, higher means more suspicious
            - matched_patterns: List of pattern descriptions that matched
    """
    if not user_input or len(user_input.strip()) == 0:
        return False, 0.0, []
    
    matched_patterns = []
    suspicion_score = 0.0
    
    # Check against suspicious patterns
    for pattern in SUSPICIOUS_PATTERNS:
        if re.search(pattern, user_input):
            matched_patterns.append(pattern)
            # Each match increases suspicion significantly
            suspicion_score += 0.35  # Increased from 0.2 to make single matches more significant
    
    # Additional heuristics
    
    # Check for excessive special characters (might be trying to escape context)
    special_char_ratio = len(re.findall(r'[{}()<>\[\]"\'`]', user_input)) / len(user_input)
    if special_char_ratio > 0.15:  # More than 15% special characters
        suspicion_score += 0.1
        matched_patterns.append("High ratio of special characters")
    
    # Check for multiple consecutive instruction keywords
    instruction_keywords = [
        'ignore', 'disregard', 'forget', 'override', 'system', 'admin', 
        'execute', 'run', 'eval', 'prompt', 'instruction', 'command'
    ]
    keyword_count = sum(1 for keyword in instruction_keywords if keyword in user_input.lower())
    if keyword_count >= 3:
        suspicion_score += 0.15
        matched_patterns.append(f"Multiple instruction keywords ({keyword_count})")
    
    # Check for unusual capitalization patterns (YELLING might be trying to emphasize commands)
    if len(user_input) > 20:
        upper_ratio = sum(1 for c in user_input if c.isupper()) / len(user_input)
        if upper_ratio > 0.5:  # More than 50% uppercase
            suspicion_score += 0.05
            matched_patterns.append("Unusual capitalization pattern")
    
    # Normalize score to 0-1 range
    suspicion_score = min(suspicion_score, 1.0)
    
    # Determine if input is suspicious
    is_suspicious = suspicion_score >= threshold
    
    if is_suspicious:
        logging.warning(
            f"Potential prompt injection detected: score={suspicion_score:.2f}, "
            f"patterns={len(matched_patterns)}, preview={user_input[:100]}"
        )
    
    return is_suspicious, suspicion_score, matched_patterns


def sanitize_for_llm_input(user_input: str) -> str:
    """
    Sanitize user input before passing to LLM to reduce prompt injection risk.
    
    This function:
    - Limits input length
    - Escapes special characters
    - Removes potential control sequences
    
    Args:
        user_input: Raw user input
        
    Returns:
        Sanitized input safe for LLM processing
    """
    if not user_input:
        return ""
    
    # Limit input length (reasonable maximum for feedback)
    max_length = 2000
    if len(user_input) > max_length:
        user_input = user_input[:max_length]
        logging.info(f"Input truncated from {len(user_input)} to {max_length} characters")
    
    # Remove potential control characters and escape sequences
    # Keep only printable characters, spaces, and basic punctuation
    sanitized = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]', '', user_input)
    
    # Normalize whitespace
    sanitized = re.sub(r'\s+', ' ', sanitized)
    
    return sanitized.strip()


def validate_user_feedback(feedback_text: str, sources: list) -> tuple[bool, str]:
    """
    Validate user feedback for potential security issues before processing.
    
    Args:
        feedback_text: User-provided feedback text
        sources: List of user-provided source URLs
        
    Returns:
        tuple: (is_valid, error_message)
            - is_valid: True if feedback passes validation
            - error_message: Description of validation failure, or empty string if valid
    """
    # Check for empty input
    if not feedback_text or len(feedback_text.strip()) < 10:
        return False, "Feedback must be at least 10 characters long."
    
    # Check for excessive length
    if len(feedback_text) > 2000:
        return False, "Feedback must be 2000 characters or less."
    
    # Check for prompt injection
    is_suspicious, score, patterns = detect_prompt_injection(feedback_text, threshold=0.3)
    if is_suspicious:
        logging.warning(
            f"Rejected suspicious feedback - score: {score:.2f}, "
            f"patterns: {len(patterns)}, text: {feedback_text[:100]}..."
        )
        return False, "Your input appears to contain instructions or commands. Please provide factual information only."
    
    # Validate sources
    if sources:
        for source in sources:
            # Check source length
            if len(source) > 500:
                return False, "Source URLs must be 500 characters or less."
            
            # Check for suspicious patterns in sources too
            is_suspicious, score, _ = detect_prompt_injection(source, threshold=0.7)
            if is_suspicious:
                return False, "Source contains suspicious content. Please provide valid URLs only."
    
    return True, ""
