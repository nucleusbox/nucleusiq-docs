# Example: Basic Agent

A minimal agent with tools across two providers.

*Updated for v0.7.6: `prompt` is now mandatory.*

## With MockLLM (no API key)

```python
import asyncio
from nucleusiq.agents import Agent
from nucleusiq.prompts.zero_shot import ZeroShotPrompt
from nucleusiq.core.llms.mock_llm import MockLLM

async def main():
    agent = Agent(
        name="assistant",
        prompt=ZeroShotPrompt().configure(
            system="You are a helpful assistant.",
        ),
        llm=MockLLM(),
    )
    result = await agent.execute({"id": "b1", "objective": "What is 2 + 2?"})
    print(result.output)

asyncio.run(main())
```

## With OpenAI

```python
import asyncio
from nucleusiq.agents import Agent
from nucleusiq.agents.config import AgentConfig, ExecutionMode
from nucleusiq.prompts.zero_shot import ZeroShotPrompt
from nucleusiq.tools.decorators import tool
from nucleusiq_openai import BaseOpenAI

@tool
def calculate(expression: str) -> str:
    """Evaluate a math expression."""
    return str(eval(expression))

async def main():
    agent = Agent(
        name="math-helper",
        prompt=ZeroShotPrompt().configure(
            system="You are a math assistant. Use the calculate tool for computations.",
        ),
        llm=BaseOpenAI(model_name="gpt-4.1-mini"),
        tools=[calculate],
        config=AgentConfig(execution_mode=ExecutionMode.STANDARD),
    )
    result = await agent.execute({"id": "b2", "objective": "What is 15% of $2,400?"})
    print(result.output)
    print(agent.last_usage.display())

asyncio.run(main())
```

## With Gemini

```python
import asyncio
from nucleusiq.agents import Agent
from nucleusiq.agents.config import AgentConfig, ExecutionMode
from nucleusiq.prompts.zero_shot import ZeroShotPrompt
from nucleusiq_gemini import BaseGemini, GeminiTool

async def main():
    agent = Agent(
        name="researcher",
        prompt=ZeroShotPrompt().configure(
            system="Answer with the latest information from the web.",
        ),
        llm=BaseGemini(model_name="gemini-2.5-flash"),
        tools=[GeminiTool.google_search()],
        config=AgentConfig(execution_mode=ExecutionMode.STANDARD),
    )
    result = await agent.execute({"id": "b3", "objective": "What are the latest developments in AI?"})
    print(result.output)

asyncio.run(main())
```

## With Context Management

*New in v0.7.6*

For tool-heavy agents that make many tool calls:

```python
import asyncio
from nucleusiq.agents import Agent
from nucleusiq.agents.config import AgentConfig, ExecutionMode
from nucleusiq.agents.context import ContextConfig, ContextStrategy
from nucleusiq.prompts.zero_shot import ZeroShotPrompt
from nucleusiq_openai import BaseOpenAI

async def main():
    agent = Agent(
        name="analyst",
        prompt=ZeroShotPrompt().configure(
            system="You are a research analyst. Gather data using tools, then write a comprehensive report.",
        ),
        llm=BaseOpenAI(model_name="gpt-4.1-mini"),
        tools=[...],
        config=AgentConfig(
            execution_mode=ExecutionMode.STANDARD,
            context=ContextConfig(
                optimal_budget=50_000,
                strategy=ContextStrategy.PROGRESSIVE,
            ),
        ),
    )
    result = await agent.execute({"id": "b4", "objective": "Analyze TCS annual report"})
    print(result.output)

    if result.context_telemetry:
        print(f"Peak utilization: {result.context_telemetry.peak_utilization:.1%}")

asyncio.run(main())
```

## See also

- [Quickstart](../quickstart.md) — Full setup guide
- [Context management](../context-management.md) — Context window management guide
- [Gemini quickstart](gemini-quickstart.md) — All three gearbox modes with Gemini
