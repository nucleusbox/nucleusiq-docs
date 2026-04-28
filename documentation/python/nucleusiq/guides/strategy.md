# Strategy Guide

NucleusIQ strategy starts with selecting the right execution mode.

## Gearbox strategy

| Mode | Best for | Tool budget |
|------|----------|-------------|
| DIRECT | Fast answers, simple requests | up to 5 |
| STANDARD | Most production workflows | up to 30 |
| AUTONOMOUS | Complex/high-stakes workflows | up to 100 |

```python
from nucleusiq.agents.config import AgentConfig, ExecutionMode

config = AgentConfig(execution_mode=ExecutionMode.STANDARD)
```

## Selection heuristic

- Start with **STANDARD** for most use cases.
- Use **DIRECT** when latency and cost are critical and workflow is simple.
- Use **AUTONOMOUS** for decomposition/verification-heavy tasks.

## Production guardrails

Combine mode choice with plugins:

```python
from nucleusiq.agents import Agent
from nucleusiq.agents.config import AgentConfig, ExecutionMode
from nucleusiq.prompts.zero_shot import ZeroShotPrompt
from nucleusiq.plugins.builtin import ModelCallLimitPlugin, ToolRetryPlugin
from nucleusiq_openai import BaseOpenAI

agent = Agent(
    name="strategy-guardrails",
    prompt=ZeroShotPrompt().configure(system="You are a helpful assistant."),
    llm=BaseOpenAI(model_name="gpt-4.1-mini"),
    plugins=[
        ModelCallLimitPlugin(max_calls=15),
        ToolRetryPlugin(max_retries=2),
    ],
    config=AgentConfig(execution_mode=ExecutionMode.STANDARD),
)
```
