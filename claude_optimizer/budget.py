"""
Cost calculation and token budget tracking for Claude models.
"""

from dataclasses import dataclass
from typing import Dict, Optional


@dataclass
class ModelCost:
    input_per_million: float
    output_per_million: float
    cache_write_per_million: float
    cache_read_per_million: float


# Official Anthropic standard pricing benchmarks (USD per 1M tokens)
CLAUDE_PRICING: Dict[str, ModelCost] = {
    "claude-3-5-sonnet": ModelCost(
        input_per_million=3.00,
        output_per_million=15.00,
        cache_write_per_million=3.75,
        cache_read_per_million=0.30,
    ),
    "claude-3-5-haiku": ModelCost(
        input_per_million=1.00,
        output_per_million=5.00,
        cache_write_per_million=1.25,
        cache_read_per_million=0.10,
    ),
    "claude-3-opus": ModelCost(
        input_per_million=15.00,
        output_per_million=75.00,
        cache_write_per_million=18.75,
        cache_read_per_million=1.50,
    ),
}


class ClaudeModelPricing:
    @staticmethod
    def calculate_cost(
        model: str,
        input_tokens: int,
        output_tokens: int,
        cache_write_tokens: int = 0,
        cache_read_tokens: int = 0,
    ) -> float:
        """Calculates exact API cost in USD based on token counts."""
        key = model.lower()
        pricing = CLAUDE_PRICING.get(key)
        if not pricing:
            # Fallback to 3.5 Sonnet pricing if unknown model
            pricing = CLAUDE_PRICING["claude-3-5-sonnet"]

        cost = (
            (input_tokens / 1_000_000) * pricing.input_per_million
            + (output_tokens / 1_000_000) * pricing.output_per_million
            + (cache_write_tokens / 1_000_000) * pricing.cache_write_per_million
            + (cache_read_tokens / 1_000_000) * pricing.cache_read_per_million
        )
        return round(cost, 6)


class TokenBudgetTracker:
    """Tracks token consumption across sessions and enforces expenditure limits."""

    def __init__(self, max_tokens: int = 200_000, max_budget_usd: Optional[float] = None, model: str = "claude-3-5-sonnet"):
        self.max_tokens = max_tokens
        self.max_budget_usd = max_budget_usd
        self.model = model

        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.total_cache_read_tokens = 0
        self.total_cache_write_tokens = 0

    def record_usage(
        self,
        input_tokens: int,
        output_tokens: int,
        cache_read_tokens: int = 0,
        cache_write_tokens: int = 0,
    ) -> None:
        """Records token usage from an Anthropic API response."""
        self.total_input_tokens += input_tokens
        self.total_output_tokens += output_tokens
        self.total_cache_read_tokens += cache_read_tokens
        self.total_cache_write_tokens += cache_write_tokens

    @property
    def total_tokens(self) -> int:
        return self.total_input_tokens + self.total_output_tokens

    @property
    def total_cost_usd(self) -> float:
        return ClaudeModelPricing.calculate_cost(
            model=self.model,
            input_tokens=self.total_input_tokens,
            output_tokens=self.total_output_tokens,
            cache_write_tokens=self.total_cache_write_tokens,
            cache_read_tokens=self.total_cache_read_tokens,
        )

    def is_over_budget(self) -> bool:
        if self.total_tokens >= self.max_tokens:
            return True
        if self.max_budget_usd is not None and self.total_cost_usd >= self.max_budget_usd:
            return True
        return False

    def remaining_token_allowance(self) -> int:
        return max(0, self.max_tokens - self.total_tokens)
