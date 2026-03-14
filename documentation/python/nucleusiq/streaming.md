# Streaming

Stream real-time output from agent runs with `execute_stream()`.

## Basic usage

```python
from nucleusiq.agents import StreamEventType

async for event in agent.execute_stream(task):
    if event.type == StreamEventType.TOKEN:
        print(event.token, end="")
    elif event.type == StreamEventType.TOOL_CALL_START:
        print(f"\n[Tool: {event.tool_name}]")
```

## Robust stream consumer

```python
from nucleusiq.agents import StreamEventType

chunks = []
async for event in agent.execute_stream(task):
    if event.type == StreamEventType.TOKEN and event.token:
        chunks.append(event.token)
        print(event.token, end="", flush=True)
    elif event.type == StreamEventType.COMPLETE:
        print("\n[done]")
    elif event.type == StreamEventType.ERROR:
        raise RuntimeError(event.message or "Streaming failed")

final_text = "".join(chunks)
```

## Event types

| Event | Description |
|-------|-------------|
| `TOKEN` | Text chunk from the LLM |
| `TOOL_CALL_START` | Agent started a tool call |
| `TOOL_CALL_END` | Tool call finished |
| `LLM_CALL_START` | LLM call started |
| `LLM_CALL_END` | LLM call finished |
| `THINKING` | Reasoning tokens (if supported) |
| `COMPLETE` | Execution finished |
| `ERROR` | Error occurred |

## All execution modes

Streaming works across Direct, Standard, and Autonomous modes—including tool call visibility.

## See also

- [Agents](agents.md) — Agent lifecycle
- [Execution modes](execution-modes.md) — Mode behavior
