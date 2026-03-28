# Memory

NucleusIQ agents support conversation memory across turns. Choose a strategy that fits your workload. All strategies work identically with any LLM provider (OpenAI, Gemini, MockLLM).

## Strategies

| Strategy | Use case | How it works |
|----------|----------|-------------|
| `FULL_HISTORY` | Short conversations | Keeps all messages |
| `SLIDING_WINDOW` | Chat applications | Keeps last N messages |
| `SUMMARY` | Long conversations | Summarizes older turns via LLM |
| `SUMMARY_WINDOW` | Long-running assistants | Summary of old + recent window |
| `TOKEN_BUDGET` | Hard cost control | Keeps messages within token budget |

## Configuration

```python
from nucleusiq.agents import Agent
from nucleusiq.memory import MemoryFactory, MemoryStrategy

memory = MemoryFactory.create_memory(
    MemoryStrategy.SLIDING_WINDOW,
    window_size=10,
)

agent = Agent(..., memory=memory)
```

## Strategy examples

```python
from nucleusiq.memory import MemoryFactory, MemoryStrategy

# Keep everything (default)
full = MemoryFactory.create_memory(MemoryStrategy.FULL_HISTORY)

# Last 12 messages
windowed = MemoryFactory.create_memory(MemoryStrategy.SLIDING_WINDOW, window_size=12)

# Hard token limit
budgeted = MemoryFactory.create_memory(MemoryStrategy.TOKEN_BUDGET, max_tokens=4096)

# Summarize old messages (requires an LLM)
summary = MemoryFactory.create_memory(MemoryStrategy.SUMMARY)

# Summary + recent window (best of both)
hybrid = MemoryFactory.create_memory(MemoryStrategy.SUMMARY_WINDOW, window_size=8)
```

**Recommendations:**

- **`SLIDING_WINDOW`** for most chat apps
- **`TOKEN_BUDGET`** when you need hard cost limits
- **`SUMMARY_WINDOW`** for long-running assistants that need both context and efficiency

## File-aware metadata

All strategies store attachment metadata alongside messages. User messages with attachments get a `[Attached: ...]` summary prefix for context continuity across turns.

## See also

- [Agents](agents.md) — Agent configuration
- [Attachments](attachments.md) — Multimodal inputs
- [Usage tracking](usage-tracking.md) — Monitor token consumption
