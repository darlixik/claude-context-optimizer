"""
Context pruning strategies to fit large prompt sequences within target token budgets.
"""

from enum import Enum
from typing import List, Dict, Any
from .tokenizer import estimate_tokens, estimate_messages_tokens


class PruneStrategy(str, Enum):
    SLIDING_WINDOW = "sliding_window"
    PRESERVE_SYSTEM_AND_RECENT = "preserve_system_and_recent"
    CODE_COMPACT = "code_compact"


class ContextPruner:
    """Intelligently truncates or trims conversation histories to satisfy a token budget."""

    def __init__(self, target_token_limit: int = 150_000, strategy: PruneStrategy = PruneStrategy.PRESERVE_SYSTEM_AND_RECENT):
        self.target_token_limit = target_token_limit
        self.strategy = strategy

    def prune_messages(self, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Prunes message history to ensure total tokens stay below target_token_limit.
        Always preserves the initial system prompt / user instruction and the latest exchange.
        """
        current_tokens = estimate_messages_tokens(messages)
        if current_tokens <= self.target_token_limit or len(messages) <= 2:
            return messages

        if self.strategy == PruneStrategy.PRESERVE_SYSTEM_AND_RECENT:
            first_msg = messages[0]
            recent_msgs = messages[1:]

            # Remove messages from the middle until we fit the budget
            while recent_msgs and estimate_messages_tokens([first_msg] + recent_msgs) > self.target_token_limit:
                if len(recent_msgs) <= 1:
                    break
                # Pop the oldest non-initial message
                recent_msgs.pop(0)

            return [first_msg] + recent_msgs

        elif self.strategy == PruneStrategy.SLIDING_WINDOW:
            trimmed = list(messages)
            while trimmed and estimate_messages_tokens(trimmed) > self.target_token_limit:
                if len(trimmed) <= 1:
                    break
                trimmed.pop(0)
            return trimmed

        return messages

    @staticmethod
    def compact_code_blocks(text: str, max_lines_per_block: int = 40) -> str:
        """
        Compacts excessive code snippet output inside markdown fences to save tokens.
        """
        lines = text.split("\n")
        in_code_block = False
        block_lines = []
        result = []

        for line in lines:
            if line.strip().startswith("```"):
                if in_code_block:
                    # Closing fence
                    if len(block_lines) > max_lines_per_block:
                        half = max_lines_per_block // 2
                        result.extend(block_lines[:half])
                        result.append(f"\n... [Truncated {len(block_lines) - max_lines_per_block} lines to conserve context] ...\n")
                        result.extend(block_lines[-half:])
                    else:
                        result.extend(block_lines)
                    block_lines = []
                    result.append(line)
                    in_code_block = False
                else:
                    # Opening fence
                    in_code_block = True
                    result.append(line)
            elif in_code_block:
                block_lines.append(line)
            else:
                result.append(line)

        if in_code_block and block_lines:
            result.extend(block_lines)

        return "\n".join(result)
