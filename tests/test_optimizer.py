import unittest
from claude_optimizer.tokenizer import estimate_tokens, estimate_messages_tokens
from claude_optimizer.budget import ClaudeModelPricing, TokenBudgetTracker
from claude_optimizer.pruner import ContextPruner, PruneStrategy


class TestClaudeOptimizer(unittest.TestCase):
    def test_token_estimation(self):
        text = "Hello Claude, can you optimize this context window for me?"
        tokens = estimate_tokens(text)
        self.assertGreater(tokens, 5)
        self.assertLess(tokens, 30)

    def test_pricing_calculation(self):
        # 1M input tokens on 3.5 Sonnet = $3.00
        cost = ClaudeModelPricing.calculate_cost("claude-3-5-sonnet", input_tokens=1_000_000, output_tokens=0)
        self.assertAlmostEqual(cost, 3.00, places=2)

    def test_budget_tracker_limit(self):
        tracker = TokenBudgetTracker(max_tokens=10_000, max_budget_usd=0.05, model="claude-3-5-sonnet")
        tracker.record_usage(input_tokens=5_000, output_tokens=1_000)
        self.assertFalse(tracker.is_over_budget())

        # Push past token budget
        tracker.record_usage(input_tokens=10_000, output_tokens=2_000)
        self.assertTrue(tracker.is_over_budget())

    def test_context_pruner(self):
        messages = [
            {"role": "user", "content": "Initial system instructions and project requirements."},
            {"role": "assistant", "content": "Acknowledged. Let's begin the multi-turn session."},
            {"role": "user", "content": "Here is an intermediate question that can be purged later."},
            {"role": "assistant", "content": "Here is an intermediate answer."},
            {"role": "user", "content": "Latest query: what is the final verdict?"},
        ]
        pruner = ContextPruner(target_token_limit=30, strategy=PruneStrategy.PRESERVE_SYSTEM_AND_RECENT)
        pruned = pruner.prune_messages(messages)
        self.assertLessEqual(len(pruned), len(messages))
        self.assertEqual(pruned[0]["content"], messages[0]["content"])
        self.assertEqual(pruned[-1]["content"], messages[-1]["content"])


if __name__ == "__main__":
    unittest.main()
