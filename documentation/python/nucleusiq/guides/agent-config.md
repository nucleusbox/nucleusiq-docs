# AgentConfig guide

`AgentConfig` controls execution behavior, budgets, quality settings, context management, and observability.

## Key fields

```python
from nucleusiq.agents.config import AgentConfig, ExecutionMode

config = AgentConfig(
    execution_mode=ExecutionMode.STANDARD,
    max_tool_calls=30,
    llm_max_output_tokens=2048,
    llm_call_timeout=90,
    step_timeout=60,
    max_retries=3,
    verbose=False,
)
```

| Field | Default | Description |
|-------|---------|-------------|
| `execution_mode` | `STANDARD` | Direct, Standard, or Autonomous |
| `max_tool_calls` | Mode-based (5/30/100) | Maximum tool calls per execution |
| `llm_max_output_tokens` | `None` | Max output tokens per LLM call |
| `llm_call_timeout` | `60` | Timeout per LLM call (seconds) |
| `step_timeout` | `30` | Timeout per tool step (seconds) |
| `max_retries` | `3` | Retry count for failed operations |
| `max_iterations` | `5` | Max iterations (Autonomous mode) |
| `require_quality_check` | `False` | Enable Critic/Refiner (Autonomous) |
| `verbose` | `False` | Print debug logs |
| `enable_tracing` | `False` | Enable ExecutionTracer |
| `enable_synthesis` | `True` | Enable synthesis pass after multi-round tool loops (v0.7.6). From **v0.7.7**, when the **tool-call cap** is reached, Standard mode still runs a **tools-free synthesis** step if synthesis is enabled, so validation/refinement can proceed. |
| `context` | `None` | `ContextConfig` for context window management (v0.7.6; **v0.7.7** stabilizes V2 compaction/masking — see [Context management](../context-management.md)) |
| `observability` | `None` | `ObservabilityConfig` for unified tracing/logging (v0.7.6) |

## Context window management

*New in v0.7.6*

Add context management to prevent context overflow in tool-heavy agents:

```python
from nucleusiq.agents.context import ContextConfig, ContextStrategy

config = AgentConfig(
    context=ContextConfig(
        optimal_budget=50_000,
        strategy=ContextStrategy.PROGRESSIVE,
    ),
)
```

See [Context management](../context-management.md) for configuration options and telemetry.

## Synthesis pass

*New in v0.7.6*

After multiple rounds of tool calls, the agent makes one final LLM call **without tools** to produce the full deliverable. This prevents the "mode inertia" problem where the model keeps calling tools instead of writing the final answer.

```python
config = AgentConfig(
    enable_synthesis=True,  # Default: True
)
```

Set `enable_synthesis=False` to disable.

## ObservabilityConfig

*New in v0.7.6*

Unified observability configuration that replaces the separate `verbose` and `enable_tracing` fields:

```python
from nucleusiq.agents.config.observability_config import ObservabilityConfig

config = AgentConfig(
    observability=ObservabilityConfig(
        tracing=True,
        verbose=True,
        log_level="DEBUG",
        log_llm_calls=True,
        log_tool_results=True,
    ),
)
```

| Field | Default | Description |
|-------|---------|-------------|
| `tracing` | `False` | Enable execution tracing |
| `verbose` | `False` | Enable debug logging |
| `log_level` | `"INFO"` | Logger level |
| `log_llm_calls` | `False` | Log LLM call details |
| `log_tool_results` | `False` | Log tool execution results |

When `observability` is set, it takes precedence over the legacy `verbose` and `enable_tracing` fields. You can use either approach — they are backward compatible.

## LLM parameter overrides

Use typed provider params for advanced control:

=== "OpenAI"

    ```python
    from nucleusiq_openai import OpenAILLMParams

    config = AgentConfig(
        llm_params=OpenAILLMParams(
            temperature=0.2,
            reasoning_effort="low",
        ),
    )
    ```

=== "Gemini"

    ```python
    from nucleusiq_gemini import GeminiLLMParams, GeminiThinkingConfig

    config = AgentConfig(
        llm_params=GeminiLLMParams(
            temperature=0.5,
            thinking_config=GeminiThinkingConfig(thinking_budget=2048),
        ),
    )
    ```

## Execution tracing

Enable tracing to populate detailed execution data in `AgentResult`:

```python
config = AgentConfig(
    execution_mode=ExecutionMode.STANDARD,
    enable_tracing=True,
)

result = await agent.execute(task)

for tool_call in result.tool_calls:
    print(f"{tool_call['name']}: {tool_call['duration_ms']}ms")

# Context telemetry (v0.7.6)
if result.context_telemetry:
    print(f"Peak utilization: {result.context_telemetry.peak_utilization:.1%}")
```

Tracing is zero-overhead when disabled (the default).

## Per-task overrides

Override parameters for a single execution without changing the agent config:

```python
from nucleusiq_openai import OpenAILLMParams

result = await agent.execute(
    {"id": "agent-config-1", "objective": "Generate a precise summary"},
    llm_params=OpenAILLMParams(temperature=0.0),
)
```

## Mode-sensitive tool budget

If `max_tool_calls` is not set, defaults are mode-based:

| Mode | Default tool limit |
|------|--------------------|
| DIRECT | 5 |
| STANDARD | 30 |
| AUTONOMOUS | 100 |

```python
effective = config.get_effective_max_tool_calls()
```

## See also

- [Context management](../context-management.md) — Full context window management guide
- [Execution modes](../execution-modes.md) — Mode behavior and selection
- [Observability](../observability/index.md) — Tracing, usage, and cost
- [Models](../models.md) — Provider-specific parameters
- [Providers](../providers.md) — Provider portability
