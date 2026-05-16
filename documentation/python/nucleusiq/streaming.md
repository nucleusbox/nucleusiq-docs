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

- **OpenAI** — Supports streaming for both Chat Completions and Responses API; **429** responses honor **`Retry-After`** via **`retry_policy`** (**v0.7.9+**, **`nucleusiq-openai` 0.6.4+).
- **Gemini** — Supports streaming with `THINKING` events for 2.5+ models when thinking mode is enabled; **429** with **`Retry-After`** merges **`retry_policy`** sleeps (**v0.7.9+**, **`nucleusiq-gemini` 0.2.6+).
- **Anthropic** — **`execute_stream()`** via Messages streaming; mapped to **`StreamEvent`** (**`nucleusiq-anthropic`**, **alpha**). **`call_stream`** ignores Agent **`response_format`** with a **warning** (use non-stream paths or manual parsing for structured deltas).
- **Groq** — Chat Completions streaming via **`nucleusiq-groq`**; streaming session **open** shares the same **429** / **`Retry-After`** policy as non-stream chat (**v0.7.9+**, **`nucleusiq-groq` 0.1.0b1+).
- **Ollama** — **`execute_stream()`** over **`/api/chat`**; **`THINKING`** events when **`think`** is set on **`OllamaLLMParams`** (**`nucleusiq-ollama`**, **alpha**).

## All execution modes

Streaming works across Direct, Standard, and Autonomous modes — including tool call visibility in Standard and Autonomous.

## See also

- [Streaming example](examples/streaming.md) — Full runnable examples (including Gemini thinking)
- [Agents](agents.md) — Agent lifecycle
- [Execution modes](execution-modes.md) — Mode behavior
