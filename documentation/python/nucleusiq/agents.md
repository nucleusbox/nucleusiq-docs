# Agents

An agent is a managed runtime with memory, tools, policy, streaming, structure, and responsibilities.

## Creating an agent

```python
from nucleusiq.agents import Agent
from nucleusiq.agents.config import AgentConfig, ExecutionMode
from nucleusiq_openai import BaseOpenAI

agent = Agent(
    name="analyst",
    role="Data analyst",
    objective="Answer questions and analyze data",
    llm=BaseOpenAI(model_name="gpt-4o-mini"),
    config=AgentConfig(execution_mode=ExecutionMode.STANDARD),
)
```

## Agent lifecycle

1. **Initialize** — Call `await agent.initialize()` before first use (or let `execute` do it automatically).
2. **Execute** — `task = Task(id="t1", objective="...")` then `result = await agent.execute(task)`.
3. **Stream** — `async for event in agent.execute_stream(task):` for real-time output.

## End-to-end example

```python
import asyncio
from nucleusiq.agents import Agent
from nucleusiq.agents.task import Task
from nucleusiq.agents.config import AgentConfig, ExecutionMode
from nucleusiq_openai import BaseOpenAI

async def main():
    agent = Agent(
        name="research-assistant",
        role="Research assistant",
        objective="Answer with concise, verifiable outputs",
        llm=BaseOpenAI(model_name="gpt-4o-mini"),
        config=AgentConfig(execution_mode=ExecutionMode.STANDARD),
    )
    await agent.initialize()

    task = Task(id="q1", objective="Give 3 facts about the Eiffel Tower.")
    result = await agent.execute(task)
    print(result)

asyncio.run(main())
```


## Usage tracking

After execution, inspect token usage:

```python
result = await agent.execute(task)
print(agent.last_usage.display())
# or
summary = agent.last_usage.summary()  # dict for logging/dashboards
```

`usage.by_origin` separates user tokens (initial MAIN call) from framework overhead (planning, tool loops, critic, refiner).

## See also

- [Execution modes](execution-modes.md) — Direct, Standard, Autonomous
- [Tools](tools.md) — Built-in and custom tools
- [Memory](memory.md) — Conversation history strategies
- [Usage tracking](usage-tracking.md) — UsageSummary, by-purpose and by-origin
- [Quickstart](quickstart.md) — End-to-end first run
