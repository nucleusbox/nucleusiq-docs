# Quickstart

This quickstart takes you from setup to a fully functional agent in a few minutes.

## Requirements

- Python 3.10+
- An API key for your chosen provider
- [Install](install.md) NucleusIQ and a provider package

## Minimal example (no API key)

Using the built-in `MockLLM` for testing:

```python
import asyncio
from nucleusiq.agents import Agent
from nucleusiq.prompts.zero_shot import ZeroShotPrompt
from nucleusiq.core.llms.mock_llm import MockLLM

async def main():
    llm = MockLLM()
    agent = Agent(
        name="Assistant",
        prompt=ZeroShotPrompt().configure(
            system="You are a helpful assistant.",
        ),
        llm=llm,
    )
    result = await agent.execute({"id": "q1", "objective": "What is 2 + 2?"})
    print(result.output)

asyncio.run(main())
```

## With OpenAI

```python
import asyncio
from nucleusiq.agents import Agent
from nucleusiq.agents.config import AgentConfig, ExecutionMode
from nucleusiq.prompts.zero_shot import ZeroShotPrompt
from nucleusiq_openai import BaseOpenAI

async def main():
    llm = BaseOpenAI(model_name="gpt-4.1-mini")
    agent = Agent(
        name="Assistant",
        prompt=ZeroShotPrompt().configure(
            system="You are a helpful assistant.",
        ),
        llm=llm,
        config=AgentConfig(execution_mode=ExecutionMode.STANDARD),
    )
    result = await agent.execute({"id": "q2", "objective": "What is the capital of France?"})
    print(result.output)

asyncio.run(main())
```

Set `OPENAI_API_KEY` in your environment or `.env` file.

## With Gemini

```python
import asyncio
from nucleusiq.agents import Agent
from nucleusiq.agents.config import AgentConfig, ExecutionMode
from nucleusiq.prompts.zero_shot import ZeroShotPrompt
from nucleusiq_gemini import BaseGemini

async def main():
    llm = BaseGemini(model_name="gemini-2.5-flash")
    agent = Agent(
        name="Assistant",
        prompt=ZeroShotPrompt().configure(
            system="You are a helpful assistant.",
        ),
        llm=llm,
        config=AgentConfig(execution_mode=ExecutionMode.STANDARD),
    )
    result = await agent.execute({"id": "q3", "objective": "What is the capital of France?"})
    print(result.output)

asyncio.run(main())
```

Set `GEMINI_API_KEY` in your environment or `.env` file.

## Execution modes

NucleusIQ uses the **Gearbox Strategy** — three modes that scale from simple chat to autonomous reasoning:

| Mode | Best for | Tool calls |
|------|----------|-----------|
| **DIRECT** | Fast Q&A, classification | Up to 5 |
| **STANDARD** | Tool-enabled workflows (default) | Up to 30 |
| **AUTONOMOUS** | Complex multi-step tasks with verification | Up to 100 |

```python
from nucleusiq.agents.config import AgentConfig, ExecutionMode

config = AgentConfig(execution_mode=ExecutionMode.AUTONOMOUS)
agent = Agent(prompt=prompt, llm=llm, config=config)
```

See [Execution modes](execution-modes.md) for details.

## Add tools in 60 seconds

Use the `@tool` decorator to create tools from plain functions:

```python
from nucleusiq.tools.decorators import tool

@tool
def get_weather(city: str) -> str:
    """Get current weather for a city."""
    return f"Weather in {city}: 22C, Sunny"

agent = Agent(
    name="weather-bot",
    prompt=ZeroShotPrompt().configure(system="You are a weather assistant."),
    llm=llm,
    tools=[get_weather],
    config=AgentConfig(execution_mode=ExecutionMode.STANDARD),
)
result = await agent.execute({"id": "q4", "objective": "What's the weather in Tokyo?"})
```

Or use built-in file tools:

```python
from nucleusiq.tools.builtin import FileReadTool, FileSearchTool

agent = Agent(
    name="file-reader",
    prompt=ZeroShotPrompt().configure(system="You read and analyze files."),
    llm=llm,
    tools=[
        FileReadTool(workspace_root="./workspace"),
        FileSearchTool(workspace_root="./workspace"),
    ],
)
```

## Add context management

*New in v0.7.6*

For tool-heavy agents, add context management to prevent context window overflow:

```python
from nucleusiq.agents.context import ContextConfig, ContextStrategy

agent = Agent(
    name="researcher",
    prompt=ZeroShotPrompt().configure(
        system="You are a research analyst. Gather data, then write a report.",
    ),
    llm=llm,
    tools=[...],
    config=AgentConfig(
        context=ContextConfig(
            optimal_budget=50_000,
            strategy=ContextStrategy.PROGRESSIVE,
        ),
    ),
)
```

See [Context management](context-management.md) for the full guide.

## Next steps

- [Agents](agents.md) — Agent configuration and lifecycle
- [Execution modes](execution-modes.md) — Direct vs Standard vs Autonomous
- [Prompts](prompts.md) — Prompt techniques and the mandatory prompt system
- [Context management](context-management.md) — Context window management
- [Tools](tools.md) — Built-in tools, `@tool` decorator, and provider native tools
- [Providers](providers.md) — OpenAI, Gemini, and provider portability
- [Usage tracking](usage-tracking.md) — Token usage and cost estimation
- [Plugins](plugins/overview.md) — 10 built-in plugins for guardrails and control
- [Examples](examples/index.md) — Practical patterns
