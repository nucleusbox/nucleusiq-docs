# Memory

NucleusIQ agents support conversation memory across turns. Choose a strategy that fits your workload.

## Strategies

| Strategy | Use case |
|----------|----------|
| `FULL_HISTORY` | Short conversations, full context |
| `SLIDING_WINDOW` | Limit recent messages only |
| `SUMMARY` | Long conversations, compress older turns |
| `SUMMARY_WINDOW` | Summary + recent messages |
| `TOKEN_BUDGET` | Hard token limit |

## Configuration

```python
from nucleusiq.agents import Agent
from nucleusiq.memory import MemoryFactory, MemoryStrategy

memory = MemoryFactory.create_memory(
    MemoryStrategy.SLIDING_WINDOW,
    window_size=10,
)

agent = Agent(
    ...,
    memory=memory,
)
```

## Strategy examples

```python
from nucleusiq.memory import MemoryFactory, MemoryStrategy

full_history = MemoryFactory.create_memory(MemoryStrategy.FULL_HISTORY)
windowed = MemoryFactory.create_memory(MemoryStrategy.SLIDING_WINDOW, window_size=12)
budgeted = MemoryFactory.create_memory(MemoryStrategy.TOKEN_BUDGET, max_tokens=4096)
summary = MemoryFactory.create_memory(MemoryStrategy.SUMMARY)
summary_window = MemoryFactory.create_memory(MemoryStrategy.SUMMARY_WINDOW, window_size=8)
```

Use `SLIDING_WINDOW` for most chat apps, `TOKEN_BUDGET` for hard limits, and `SUMMARY_WINDOW` for long-running assistants.

## File-aware metadata

All strategies store attachment metadata alongside messages. User messages with attachments get a `[Attached: ...]` summary prefix for context continuity.

## See also

- [Agents](agents.md) — Agent configuration
- [Attachments](attachments.md) — Multimodal inputs
