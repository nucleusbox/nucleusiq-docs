# Quickstart

This quickstart takes you from setup to a fully functional agent in a few minutes.

## Requirements

- Python 3.10+
- An API key or credentials for cloud providers — **not required** for **local Ollama** (daemon only)
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

## With Groq

Public beta inference provider — **`nucleusiq-groq` 0.1.0b1** on **`nucleusiq>=0.7.9`**. Uses Groq’s official **`groq`** SDK; pass **`async_mode=True`** on **`BaseGroq`**. Calling **`await agent.initialize()`** before **`execute()`** matches the runnable scripts in the monorepo. See also **[Groq quickstart](examples/groq-quickstart.md)** and **[Groq provider guide](guides/groq-provider.md)**.

```python
import asyncio

from nucleusiq.agents import Agent
from nucleusiq.agents.config import AgentConfig, ExecutionMode
from nucleusiq.agents.task import Task
from nucleusiq.prompts.zero_shot import ZeroShotPrompt
from nucleusiq_groq import BaseGroq, GroqLLMParams


async def main():
    llm = BaseGroq(model_name="llama-3.3-70b-versatile", async_mode=True)

    agent = Agent(
        name="Assistant",
        prompt=ZeroShotPrompt().configure(
            system="You are a helpful assistant.",
        ),
        llm=llm,
        config=AgentConfig(
            execution_mode=ExecutionMode.STANDARD,
            llm_params=GroqLLMParams(temperature=0.4, max_output_tokens=512),
        ),
    )

    await agent.initialize()

    result = await agent.execute(
        Task(id="q-groq-1", objective="What is the capital of France?"),
    )
    print(result.output)


asyncio.run(main())
```

Set **`GROQ_API_KEY`** in your environment or `.env` file. Full scope, **429** / **`Retry-After`** behavior, model-capability checks, and example scripts: [Groq provider](guides/groq-provider.md).

## With Anthropic (Claude)

!!! warning "Alpha provider"

    **`nucleusiq-anthropic` 0.1.0a1** — pre-release. Requires **`nucleusiq>=0.7.10`**, **`anthropic>=0.40,<1`**. Set **`ANTHROPIC_API_KEY`**; optional **`ANTHROPIC_MODEL`** if the default id is not enabled for your org.

Uses **`BaseAnthropic`** + **`async_mode=True`**, framework **`LLMParams`** on **`AgentConfig`** for sampling, and **`await agent.initialize()`** before **`execute()`**, matching the monorepo scripts. More patterns: **[Anthropic quickstart](examples/anthropic-quickstart.md)** and **[Anthropic provider](guides/anthropic-provider.md)**.

```python
import asyncio
import os

from nucleusiq.agents import Agent
from nucleusiq.agents.config import AgentConfig, ExecutionMode
from nucleusiq.agents.task import Task
from nucleusiq.llms.llm_params import LLMParams
from nucleusiq.prompts.zero_shot import ZeroShotPrompt
from nucleusiq_anthropic import BaseAnthropic


async def main():
    llm = BaseAnthropic(
        model_name=os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022"),
        async_mode=True,
    )

    agent = Agent(
        name="Assistant",
        prompt=ZeroShotPrompt().configure(
            system="You are a helpful assistant.",
        ),
        llm=llm,
        config=AgentConfig(
            execution_mode=ExecutionMode.STANDARD,
            llm_params=LLMParams(temperature=0.4, max_output_tokens=512),
        ),
    )

    await agent.initialize()

    result = await agent.execute(
        Task(id="q-claude-1", objective="What is the capital of France?"),
    )
    print(result.output)


asyncio.run(main())
```

## With Ollama

!!! warning "Alpha provider"

    **`nucleusiq-ollama` 0.1.0a1** — pre-release. Requires **`nucleusiq>=0.7.10`**. Run an **Ollama** daemon locally or point **`OLLAMA_HOST`** at a reachable API: `ollama pull <model>` first.

Uses **`BaseOllama`** + **`async_mode=True`** and **`await agent.initialize()`** like the monorepo scripts. More patterns: **[Ollama quickstart](examples/ollama-quickstart.md)** and **[Ollama provider](guides/ollama-provider.md)**.

```python
import asyncio
import os

from nucleusiq.agents import Agent
from nucleusiq.agents.config import AgentConfig, ExecutionMode
from nucleusiq.agents.task import Task
from nucleusiq.prompts.zero_shot import ZeroShotPrompt
from nucleusiq_ollama import BaseOllama, OllamaLLMParams


async def main():
    llm = BaseOllama(model_name=os.getenv("OLLAMA_MODEL", "llama3.2"), async_mode=True)

    agent = Agent(
        name="Assistant",
        prompt=ZeroShotPrompt().configure(
            system="You are a helpful assistant.",
        ),
        llm=llm,
        config=AgentConfig(
            execution_mode=ExecutionMode.STANDARD,
            llm_params=OllamaLLMParams(temperature=0.4, max_output_tokens=512),
        ),
    )

    await agent.initialize()

    result = await agent.execute(
        Task(id="q-ollama-1", objective="What is the capital of France?"),
    )
    print(result.output)


asyncio.run(main())
```

## Execution modes

NucleusIQ uses the **Gearbox Strategy** — three modes that scale from simple chat to autonomous reasoning:

| Mode | Best for | Default tool budget |
|------|----------|---------------------|
| **DIRECT** | Fast Q&A, classification | 25 invocations / run |
| **STANDARD** | Tool-enabled workflows (default) | 80 invocations / run |
| **AUTONOMOUS** | Complex multi-step tasks with verification | 300 invocations / run |

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
from nucleusiq.tools.builtin import FileReadTool, FileSearchTool

agent = Agent(
    name="researcher",
    prompt=ZeroShotPrompt().configure(
        system="You are a research analyst. Gather data, then write a report.",
    ),
    llm=llm,
    tools=[
        FileReadTool(workspace_root="./workspace"),
        FileSearchTool(workspace_root="./workspace"),
    ],
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
- [Providers](providers.md) — OpenAI, Gemini, Anthropic, Groq, Ollama, and provider portability
- [Usage tracking](usage-tracking.md) — Token usage and cost estimation
- [Plugins](plugins/overview.md) — 10 built-in plugins for guardrails and control
- [Examples](examples/index.md) — Practical patterns (**[Anthropic quickstart](examples/anthropic-quickstart.md)**, **[Groq quickstart](examples/groq-quickstart.md)**, **[Ollama quickstart](examples/ollama-quickstart.md)**)
