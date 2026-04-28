# Agent Guide

## Agent anatomy

*Changed in v0.7.6: `prompt` is mandatory. `role` and `objective` are labels only.*

Every agent has a clear structure — an identity, a prompt, an LLM backend, and optional tools, config, memory, and plugins:

```python
from nucleusiq.agents import Agent
from nucleusiq.agents.config import AgentConfig, ExecutionMode
from nucleusiq.prompts.zero_shot import ZeroShotPrompt
from nucleusiq_openai import BaseOpenAI

agent = Agent(
    name="analyst",               # identity
    role="Data analyst",          # label for logging — NOT sent to LLM
    objective="Analyze data",     # label for docs — NOT sent to LLM
    prompt=ZeroShotPrompt().configure(
        system="You are a data analyst. Provide thorough, evidence-based analysis.",
    ),                            # REQUIRED — defines what the LLM sees
    llm=BaseOpenAI(model_name="gpt-4.1-mini"),
    config=AgentConfig(execution_mode=ExecutionMode.STANDARD),
)
# Optional: add tools=, memory=, plugins= as needed.
```

| Field | Required | Sent to LLM? | Purpose |
|-------|----------|--------------|---------|
| `name` | Yes | No | Human-readable identifier |
| `prompt` | **Yes** | **Yes** | System message and optional user preamble — the single source of truth for what the LLM sees |
| `llm` | Yes | — | Model backend (`BaseOpenAI`, `BaseGemini`, `MockLLM`) |
| `role` | No | **No** | Label for logging and sub-agent naming. Default: `"Agent"` |
| `objective` | No | **No** | Label for documentation. Default: `""` |
| `config` | No | — | Execution mode, timeouts, context management, observability |
| `tools` | No | — | Tools the agent can call |
| `memory` | No | — | Conversation history strategy |
| `plugins` | No | — | Policy and guardrails |

!!! warning "prompt is the single source of truth"
    Everything the LLM sees comes from `prompt.system` (system message) and `prompt.user` (optional preamble). Put all LLM instructions in the prompt — not in `role` or `objective`.

## Lifecycle pattern

Create the agent, then execute tasks:

```python
import asyncio
from nucleusiq.agents import Agent
from nucleusiq.agents.task import Task
from nucleusiq.prompts.zero_shot import ZeroShotPrompt
from nucleusiq_openai import BaseOpenAI

async def main():
    agent = Agent(
        name="assistant",
        prompt=ZeroShotPrompt().configure(
            system="You are a helpful assistant.",
        ),
        llm=BaseOpenAI(model_name="gpt-4.1-mini"),
    )

    # Execute a task
    result = await agent.execute(Task(id="t1", objective="What is the capital of Japan?"))
    print(result.output)    # "The capital of Japan is Tokyo."
    print(result.status)    # ResultStatus.SUCCESS
    print(result.duration_ms)  # e.g. 1,230

    # Execute another task (same agent, reusable)
    result2 = await agent.execute({"id": "t2", "objective": "What about France?"})
    print(result2.output)

asyncio.run(main())
```

You can pass either a `Task` object or a dict with `id` and `objective`.

## Streaming pattern

For real-time token-by-token output in UIs:

```python
import asyncio
from nucleusiq.agents import Agent
from nucleusiq.prompts.zero_shot import ZeroShotPrompt
from nucleusiq_openai import BaseOpenAI

async def main():
    agent = Agent(
        name="writer",
        prompt=ZeroShotPrompt().configure(
            system="You are a creative writer. Write vivid, engaging prose.",
        ),
        llm=BaseOpenAI(model_name="gpt-4.1-mini"),
    )

    async for event in agent.execute_stream({"id": "s1", "objective": "Write a haiku about the ocean"}):
        if event.type.value == "token":
            print(event.token, end="", flush=True)
        elif event.type.value == "tool_call_start":
            print(f"\n[Calling: {event.tool_name}]")
        elif event.type.value == "complete":
            print("\n--- Done ---")

asyncio.run(main())
```

## With tools

Add tools using the `@tool` decorator:

```python
from nucleusiq.agents import Agent
from nucleusiq.agents.config import AgentConfig, ExecutionMode
from nucleusiq.prompts.zero_shot import ZeroShotPrompt
from nucleusiq.tools.decorators import tool
from nucleusiq_openai import BaseOpenAI

@tool
def get_weather(city: str) -> str:
    """Get current weather for a city."""
    return f"Weather in {city}: 22°C, Sunny"

@tool
def convert_temperature(celsius: float) -> str:
    """Convert Celsius to Fahrenheit."""
    return f"{celsius}°C = {celsius * 9/5 + 32}°F"

agent = Agent(
    name="weather-bot",
    prompt=ZeroShotPrompt().configure(
        system="You are a weather assistant. Use tools to look up weather and convert temperatures.",
    ),
    llm=BaseOpenAI(model_name="gpt-4.1-mini"),
    tools=[get_weather, convert_temperature],
    config=AgentConfig(execution_mode=ExecutionMode.STANDARD),
)
```

## With context management

*New in v0.7.6*

For tool-heavy agents, add context management to prevent context overflow:

```python
from nucleusiq.agents.context import ContextConfig, ContextStrategy

config = AgentConfig(
    context=ContextConfig(strategy=ContextStrategy.PROGRESSIVE),
)
```

See [Context management](../context-management.md) for details.

## With memory

Add conversation memory so the agent remembers previous interactions:

```python
from nucleusiq.memory import MemoryFactory, MemoryStrategy

agent = Agent(
    name="chat-bot",
    prompt=ZeroShotPrompt().configure(
        system="You are a helpful assistant that remembers previous conversations.",
    ),
    llm=llm,
    memory=MemoryFactory.create_memory(MemoryStrategy.SLIDING_WINDOW, max_messages=20),
)
```

## With plugins

Add plugins for guardrails and policy:

```python
from nucleusiq.plugins.builtin import ModelCallLimitPlugin, ToolGuardPlugin

agent = Agent(
    name="guarded-bot",
    prompt=ZeroShotPrompt().configure(
        system="You are a helpful assistant.",
    ),
    llm=llm,
    plugins=[
        ModelCallLimitPlugin(max_calls=10),
        ToolGuardPlugin(allowed_tools=["get_weather", "search"]),
    ],
)
```

## See also

- [Agent Config](agent-config.md) — Configuration reference
- [Context management](../context-management.md) — Context window management
- [Prompts](../prompts.md) — Prompt techniques
- [Execution modes](../execution-modes.md) — Direct, Standard, Autonomous
- [Tools](../tools.md) — `@tool` decorator, built-in tools, provider native tools
- [Memory](../memory.md) — Conversation history strategies
- [Plugins](../plugins/overview.md) — 10 built-in plugins
