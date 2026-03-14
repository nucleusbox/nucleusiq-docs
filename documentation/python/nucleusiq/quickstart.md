# Quickstart

This quickstart takes you from setup to a fully functional agent in a few minutes.

## Requirements

- Python 3.10+
- For OpenAI: `OPENAI_API_KEY` in your environment or `.env` file
- [Install](install.md) NucleusIQ and the OpenAI provider

## Minimal example (no API key)

Using the built-in `MockLLM` for testing:

```python
import asyncio
from nucleusiq.agents import Agent
from nucleusiq.core.llms.mock_llm import MockLLM

async def main():
    llm = MockLLM()
    agent = Agent(
        name="Assistant",
        role="Helper",
        objective="Answer questions",
        llm=llm,
    )
    await agent.initialize()

    from nucleusiq.agents.task import Task
    task = Task(id="t1", objective="What is 2 + 2?")
    result = await agent.execute(task)
    print(result)

asyncio.run(main())
```

## With OpenAI

```python
import asyncio
from nucleusiq.agents import Agent
from nucleusiq.agents.task import Task
from nucleusiq.agents.config import AgentConfig
from nucleusiq_openai import BaseOpenAI

async def main():
    llm = BaseOpenAI(model_name="gpt-4o-mini")
    agent = Agent(
        name="Assistant",
        role="Helper",
        objective="Answer questions",
        llm=llm,
        config=AgentConfig(verbose=False),
    )
    await agent.initialize()

    task = Task(id="t1", objective="What is the capital of France?")
    result = await agent.execute(task)
    print(result)

asyncio.run(main())
```

Set `OPENAI_API_KEY` in your environment or `.env` file.

## Execution modes

- **DIRECT** (default for simple tasks): Fast, single LLM call, up to 5 tool calls
- **STANDARD**: Tool-enabled, linear execution, up to 30 tool calls
- **AUTONOMOUS**: Planning, multi-step execution with Critic/Refiner, up to 100 tool calls

```python
from nucleusiq.agents.config import AgentConfig, ExecutionMode

config = AgentConfig(
    execution_mode=ExecutionMode.AUTONOMOUS,
    verbose=False,
)
agent = Agent(..., config=config)
```

See [Execution modes](execution-modes.md) for details.

## Add tools in 60 seconds

```python
from nucleusiq.tools.builtin import FileReadTool, FileSearchTool

agent = Agent(
    ...,
    tools=[
        FileReadTool(workspace_root="./workspace"),
        FileSearchTool(workspace_root="./workspace"),
    ],
)
```

## Next steps

- [Agents](agents.md) — Agent configuration and lifecycle
- [Prompts](prompts.md) — Prompt strategies and `PromptFactory`
- [Tools](tools.md) — Built-in and custom tools
- [Usage tracking](usage-tracking.md) — Token usage by purpose and origin
- [Providers](providers.md) — Provider packages and current support status
- [Examples](examples/index.md) — Curated practical patterns
- [Repository examples](https://github.com/nucleusbox/NucleusIQ/tree/main/src/nucleusiq/examples) — Full runnable scripts
