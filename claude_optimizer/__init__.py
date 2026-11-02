"""
claude-context-optimizer
~~~~~~~~~~~~~~~~~~~~~~~~
A lightweight toolkit for token tracking, context pruning, and budget management for Claude models.
"""

from .budget import TokenBudgetTracker, ClaudeModelPricing
from .pruner import ContextPruner, PruneStrategy
from .tokenizer import estimate_tokens

__version__ = "0.1.0"
__all__ = [
    "TokenBudgetTracker",
    "ClaudeModelPricing",
    "ContextPruner",
    "PruneStrategy",
    "estimate_tokens",
]
