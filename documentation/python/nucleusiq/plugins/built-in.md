# Built-in plugins

NucleusIQ includes 10 built-in plugins for common use cases.

## Plugin list

| Plugin | Purpose |
|--------|---------|
| `ModelCallLimitPlugin` | Limit total LLM calls per execution |
| `ToolCallLimitPlugin` | Limit tool calls per execution |
| `ToolRetryPlugin` | Retry failed tool calls |
| `ModelFallbackPlugin` | Fallback to a cheaper model on failure |
| `PIIGuardPlugin` | Detect and redact PII in inputs/outputs |
| `HumanApprovalPlugin` | Pause for human approval before tool execution |
| `ToolGuardPlugin` | Allow/block specific tools by policy |
| `AttachmentGuardPlugin` | Validate attachments (type, size, count) |
| `ContextWindowPlugin` | Enforce context window limits |
| `ResultValidatorPlugin` | Validate agent output against a schema |

## Example

```python
from nucleusiq.agents import Agent
from nucleusiq.agents.config import AgentConfig, ExecutionMode
from nucleusiq.prompts.zero_shot import ZeroShotPrompt
from nucleusiq.plugins.builtin import (
    ToolRetryPlugin,
    PIIGuardPlugin,
)
from nucleusiq_openai import BaseOpenAI

agent = Agent(
    name="plugins-example",
    prompt=ZeroShotPrompt().configure(system="You are a helpful assistant."),
    llm=BaseOpenAI(model_name="gpt-4.1-mini"),
    plugins=[
        ToolRetryPlugin(max_retries=2),
        PIIGuardPlugin(redact_patterns=["email", "phone"]),
    ],
    config=AgentConfig(execution_mode=ExecutionMode.STANDARD),
)
```

## ContextWindowPlugin

`ContextWindowPlugin` trims conversation history to keep messages within budget, preventing context window overflows.

### Message-count based trimming

```python
from nucleusiq.agents import Agent
from nucleusiq.agents.config import AgentConfig, ExecutionMode
from nucleusiq.prompts.zero_shot import ZeroShotPrompt
from nucleusiq.plugins.builtin import ContextWindowPlugin
from nucleusiq_openai import BaseOpenAI

llm = BaseOpenAI(model_name="gpt-4.1-mini")
agent = Agent(
    name="context-window-msgs",
    prompt=ZeroShotPrompt().configure(system="You are a helpful assistant."),
    llm=llm,
    plugins=[ContextWindowPlugin(max_messages=50, keep_recent=10)],
    config=AgentConfig(execution_mode=ExecutionMode.STANDARD),
)
```

### Token-based trimming with approximate counting (default)

```python
agent = Agent(
    name="context-window-tokens",
    prompt=ZeroShotPrompt().configure(system="You are a helpful assistant."),
    llm=llm,
    plugins=[ContextWindowPlugin(max_tokens=8000, keep_recent=5)],
    config=AgentConfig(execution_mode=ExecutionMode.STANDARD),
)
```

### Token-based trimming with provider-accurate counting

```python
agent = Agent(
    name="context-window-accurate",
    prompt=ZeroShotPrompt().configure(system="You are a helpful assistant."),
    llm=llm,
    plugins=[
        ContextWindowPlugin(
            max_tokens=8000,
            token_counter=llm.estimate_tokens,  # Uses tiktoken for OpenAI
        ),
    ],
    config=AgentConfig(execution_mode=ExecutionMode.STANDARD),
)
```

The `token_counter` parameter accepts any `(str) -> int` callable. The default uses `len(text) // 4` as a rough approximation. Providers override `estimate_tokens()` with more accurate implementations — OpenAI uses `tiktoken`, Gemini uses a heuristic.

## See also

- [Plugins overview](overview.md) — Hook points and APIs
