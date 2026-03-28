# Streaming

Stream real-time output from agent runs with `execute_stream()`. Works with all providers and all execution modes.

## Basic usage

```python
async for event in agent.execute_stream({"id": "s1", "objective": "Write a poem about the ocean"}):
    if event.type.value == "token":
        print(event.token, end="", flush=True)
    elif event.type.value == "complete":
        print("\n--- Done ---")
```

## Robust stream consumer

Handle all event types for production use:

```python
chunks = []
async for event in agent.execute_stream(task):
    match event.type.value:
        case "token":
            if event.token:
                chunks.append(event.token)
                print(event.token, end="", flush=True)
        case "tool_call_start":
            print(f"\n[Calling: {event.tool_name}]")
        case "tool_call_end":
            print(f"[Result received]")
        case "thinking":
            pass  # Gemini 2.5+ reasoning tokens (event.message)
        case "complete":
            print("\n--- Done ---")
        case "error":
            raise RuntimeError(event.message or "Streaming failed")

final_text = "".join(chunks)
```

## Event types

| Event | Description | Key field |
|-------|-------------|-----------|
| `TOKEN` | Text chunk from the LLM | `event.token` |
| `THINKING` | Reasoning tokens (Gemini 2.5+) | `event.message` |
| `TOOL_CALL_START` | Agent started a tool call | `event.tool_name`, `event.tool_args` |
| `TOOL_CALL_END` | Tool call finished | `event.tool_name`, `event.tool_result` |
| `LLM_CALL_START` | LLM call started | `event.call_count` |
| `LLM_CALL_END` | LLM call finished | `event.call_count` |
| `COMPLETE` | Execution finished | `event.content` |
| `ERROR` | Error occurred | `event.message` |

## Provider notes

- **OpenAI** — Supports streaming for both Chat Completions and Responses API
- **Gemini** — Supports streaming with `THINKING` events for 2.5+ models when thinking mode is enabled

## All execution modes

Streaming works across Direct, Standard, and Autonomous modes — including tool call visibility in Standard and Autonomous.

## See also

- [Streaming example](examples/streaming.md) — Full runnable examples with Gemini thinking
- [Agents](agents.md) — Agent lifecycle
- [Execution modes](execution-modes.md) — Mode behavior
