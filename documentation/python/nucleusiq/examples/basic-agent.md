# Example: Basic Agent

A minimal agent with tools across two providers.

## With MockLLM (no API key)

```python
import asyncio
from nucleusiq.agents import Agent
from nucleusiq.core.llms.mock_llm import MockLLM

async def main():
    agent = Agent(
        name="assistant",
        llm=MockLLM(),
        instructions="You are a helpful assistant.",
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
from nucleusiq.tools.decorators import tool
from nucleusiq_openai import BaseOpenAI

@tool
def calculate(expression: str) -> str:
    """Evaluate a math expression."""
    return str(eval(expression))

async def main():
    agent = Agent(
        name="math-helper",
        llm=BaseOpenAI(model_name="gpt-4o-mini"),
        model="gpt-4o-mini",
        instructions="You are a math assistant. Use the calculate tool for computations.",
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
from nucleusiq_gemini import BaseGemini, GeminiTool

async def main():
    agent = Agent(
        name="researcher",
        llm=BaseGemini(model_name="gemini-2.5-flash"),
        model="gemini-2.5-flash",
        instructions="Answer with the latest information from the web.",
        tools=[GeminiTool.google_search()],
        config=AgentConfig(execution_mode=ExecutionMode.STANDARD),
    )
    result = await agent.execute({"id": "b3", "objective": "What are the latest developments in AI?"})
    print(result.output)

asyncio.run(main())
```

## See also

- [Quickstart](../quickstart.md) — Full setup guide
- [Gemini quickstart](gemini-quickstart.md) — All three gearbox modes with Gemini
