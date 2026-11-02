# claude-context-optimizer

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Anthropic Claude](https://img.shields.io/badge/Anthropic-Claude%203.5-blueviolet)](https://www.anthropic.com/)

A lightweight, dependency-free developer toolkit designed to track token consumption, calculate real-time API expenditure, and optimize prompt context windows when building agents and applications powered by Anthropic's Claude models.

---

## Key Features

- **Accurate Token Estimation:** Fast, heuristic token estimation calibrated for Claude 3.5 Sonnet, Haiku, and Opus prompt structures without requiring heavy external tokenizer weights.
- **Real-Time Cost Modeling:** Built-in pricing matrices for Claude 3.5 Sonnet, Haiku, and Opus, including support for Anthropic prompt caching (cache writes and reads).
- **Intelligent Context Pruning:** Automatic multi-turn history trimming (`preserve_system_and_recent` & `sliding_window`) to keep expansive agent conversations strictly within target token boundaries.
- **Code Block Compaction:** Automatically collapses runaway terminal / code snippet outputs within markdown blocks to prevent context window bloat.
- **Zero Heavy Dependencies:** Written entirely in pure, standard-library Python for minimal latency and maximum portability.

---

## Installation

```bash
git clone https://github.com/your-username/claude-context-optimizer.git
cd claude-context-optimizer
pip install .
```

---

## Quickstart

### 1. Estimating Tokens & Cost in Code

```python
from claude_optimizer import estimate_tokens, ClaudeModelPricing

prompt = "Analyze the performance bottlenecks in this microservice architecture..."
tokens = estimate_tokens(prompt)

cost = ClaudeModelPricing.calculate_cost(
    model="claude-3-5-sonnet",
    input_tokens=tokens,
    output_tokens=1500,
    cache_read_tokens=5000
)

print(f"Tokens: {tokens}")
print(f"Estimated Cost: ${cost:.6f} USD")
```

### 2. Guarding Multi-Turn Conversations with ContextPruner

```python
from claude_optimizer import ContextPruner, PruneStrategy

messages = [
    {"role": "user", "content": "You are a senior systems engineer..."},
    {"role": "assistant", "content": "Understood."},
    # ... many conversational turns ...
    {"role": "user", "content": "How do we resolve the memory leak?"}
]

# Guarantee conversation history stays under 80,000 tokens while safeguarding initial instructions
pruner = ContextPruner(target_token_limit=80_000, strategy=PruneStrategy.PRESERVE_SYSTEM_AND_RECENT)
optimized_history = pruner.prune_messages(messages)
```

### 3. Command Line Interface (CLI)

```bash
# Analyze prompt token count and estimated cost
claude-opt estimate ./prompts/system_prompt.md --model claude-3-5-sonnet

# Calculate cost on the fly
claude-opt cost --input 45000 --output 2000 --cache-read 30000 --model claude-3-5-sonnet
```

---

## Project Structure

```
claude-context-optimizer/
├── claude_optimizer/
│   ├── __init__.py       # Package entry point
│   ├── budget.py         # Cost matrices and TokenBudgetTracker
│   ├── pruner.py         # Multi-turn context pruning algorithms
│   ├── tokenizer.py      # Token boundary estimation
│   └── cli.py            # Command-line interface
├── tests/
│   └── test_optimizer.py # Unit tests
├── pyproject.toml        # Build configuration and metadata
├── LICENSE               # MIT License
└── README.md
```

---

## Roadmap

- [ ] Support for Claude JSON Schema function/tool-use overhead estimation
- [ ] Integration hooks for LangChain and LlamaIndex message buffers
- [ ] Async budget alert webhooks for long-running batch jobs

---

## Contributing

Contributions, feedback, and pull requests are warmly welcomed! Please open an issue first to discuss what you would like to change.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## License

Distributed under the MIT License. See [LICENSE](LICENSE) for more information.
