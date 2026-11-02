"""
Token estimation utilities for Claude models.
"""

import re
from typing import Sequence, Dict, Any, Union

# Accurate rule-based heuristic token estimator (~3.8 - 4.1 chars per token in English, higher for code/whitespace)
def estimate_tokens(text: str) -> int:
    """
    Estimates the number of Claude tokens in a given text string.
    Accounts for whitespace, punctuation boundaries, and code structures.
    """
    if not text:
        return 0

    # Split roughly on word and whitespace/punctuation boundaries
    words = re.findall(r"\w+|[^\w\s]|\s+", text)
    count = 0
    for chunk in words:
        if chunk.isspace():
            count += max(1, len(chunk) // 3)
        elif len(chunk) <= 4:
            count += 1
        else:
            count += max(1, (len(chunk) + 3) // 4)

    return max(1, count)


def estimate_messages_tokens(messages: Sequence[Dict[str, Any]]) -> int:
    """
    Estimates total token footprint for a conversational message list,
    including role framing overhead.
    """
    total = 3  # Conversation start overhead
    for msg in messages:
        total += 4  # Per-message structural tokens
        content = msg.get("content", "")
        if isinstance(content, str):
            total += estimate_tokens(content)
        elif isinstance(content, list):
            for block in content:
                if isinstance(block, dict) and "text" in block:
                    total += estimate_tokens(block["text"])
    return total
