# AgentConfig guide

`AgentConfig` controls execution behavior, budgets, and quality settings.

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

- [Execution modes](../execution-modes.md) — Mode behavior and selection
- [Models](../models.md) — Provider-specific parameters
- [Providers](../providers.md) — Provider portability
