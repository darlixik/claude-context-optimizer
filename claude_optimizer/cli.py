"""
CLI tool for analyzing token usage and evaluating prompt cost.
"""

import sys
import argparse
from pathlib import Path
from .tokenizer import estimate_tokens
from .budget import ClaudeModelPricing


def main():
    parser = argparse.ArgumentParser(
        prog="claude-opt",
        description="Analyze token usage, cost estimation, and context optimization for Claude prompts."
    )
    subparsers = parser.add_subparsers(dest="command")

    # Analyze file / string command
    analyze_parser = subparsers.add_parser("estimate", help="Estimate tokens and cost for a prompt file")
    analyze_parser.add_argument("path", help="Path to text or markdown prompt file")
    analyze_parser.add_argument("--model", default="claude-3-5-sonnet", help="Claude model name (default: claude-3-5-sonnet)")

    # Cost calculator command
    cost_parser = subparsers.add_parser("cost", help="Calculate API cost given token numbers")
    cost_parser.add_argument("--input", type=int, default=0, help="Input token count")
    cost_parser.add_argument("--output", type=int, default=0, help="Output token count")
    cost_parser.add_argument("--cache-read", type=int, default=0, help="Cache read token count")
    cost_parser.add_argument("--model", default="claude-3-5-sonnet", help="Claude model name")

    args = parser.parse_args()

    if args.command == "estimate":
        filepath = Path(args.path)
        if not filepath.exists():
            print(f"Error: File '{args.path}' not found.", file=sys.stderr)
            sys.exit(1)

        content = filepath.read_text(encoding="utf-8", errors="ignore")
        tokens = estimate_tokens(content)
        cost = ClaudeModelPricing.calculate_cost(args.model, input_tokens=tokens, output_tokens=0)

        print("========================================")
        print(" Claude Context Optimizer - Analysis")
        print("========================================")
        print(f" File:           {filepath.name}")
        print(f" Character Count:{len(content):,}")
        print(f" Est. Tokens:    {tokens:,}")
        print(f" Target Model:   {args.model}")
        print(f" Est. Input Cost:${cost:.6f} USD")
        print("========================================")

    elif args.command == "cost":
        cost = ClaudeModelPricing.calculate_cost(
            model=args.model,
            input_tokens=args.input,
            output_tokens=args.output,
            cache_read_tokens=args.cache_read,
        )
        print(f"Model: {args.model}")
        print(f"Calculated Total Cost: ${cost:.6f} USD")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
