# Example: Basic Agent

```python
import asyncio
from nucleusiq.agents import Agent
from nucleusiq.agents.task import Task
from nucleusiq.llms import MockLLM

async def main():
    agent = Agent(
        name="assistant",
        role="Helper",
        objective="Answer clearly",
        llm=MockLLM(),
    )
    await agent.initialize()
    result = await agent.execute(Task(id="t1", objective="What is 2 + 2?"))
    print(result)

asyncio.run(main())
```
