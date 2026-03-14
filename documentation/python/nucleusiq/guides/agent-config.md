# AgentConfig Guide

`AgentConfig` controls execution behavior, budgets, and quality settings.

## Most important fields

```python
from nucleusiq.agents.config import AgentConfig, ExecutionMode

config = AgentConfig(
    execution_mode=ExecutionMode.STANDARD,
    max_tool_calls=30,
    llm_max_tokens=2048,
    llm_call_timeout=90,
    step_timeout=60,
    max_retries=3,
    verbose=False,
)
```

## LLM parameter overrides

Use typed params for provider-specific control:

```python
from nucleusiq.agents.config import AgentConfig
from nucleusiq_openai import OpenAILLMParams

config = AgentConfig(
    llm_params=OpenAILLMParams(temperature=0.2, reasoning_effort="low"),
)
```

## Mode-sensitive tool budget

If `max_tool_calls` is not set, defaults are mode-based.

```python
effective = config.get_effective_max_tool_calls()
```
