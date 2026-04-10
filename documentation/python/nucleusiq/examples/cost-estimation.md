# Cost estimation example

Track dollar costs of agent execution using the built-in `CostTracker`.

## Basic usage

```python
import asyncio
from nucleusiq.agents import Agent
from nucleusiq.agents.config import AgentConfig, ExecutionMode
from nucleusiq.agents.usage import CostTracker
from nucleusiq.prompts.zero_shot import ZeroShotPrompt
from nucleusiq_openai import BaseOpenAI

async def main():
    agent = Agent(
        name="assistant",
        prompt=ZeroShotPrompt().configure(
            system="You are a helpful assistant.",
        ),
        llm=BaseOpenAI(model_name="gpt-4.1-mini"),
        config=AgentConfig(execution_mode=ExecutionMode.STANDARD),
    )

    result = await agent.execute({"id": "c1", "objective": "Explain quantum computing in 3 sentences."})

    # Token usage
    usage = agent.last_usage
    print(usage.display())

    # Cost estimation
    tracker = CostTracker()
    cost = tracker.estimate(usage, model="gpt-4o-mini")
    print(f"\nEstimated cost: ${cost.total_cost:.6f}")
    print(f"  Prompt:     ${cost.prompt_cost:.6f}")
    print(f"  Completion: ${cost.completion_cost:.6f}")

asyncio.run(main())
```

## Comparing models

```python
tracker = CostTracker()
usage = agent.last_usage

for model in ["gpt-4o", "gpt-4o-mini", "gemini-2.5-flash"]:
    cost = tracker.estimate(usage, model=model)
    print(f"{model:20s} → ${cost.total_cost:.6f}")
```

## See also

- [Cost estimation docs](../observability/cost-estimation.md) — Full reference
- [Usage tracking](../usage-tracking.md) — Token usage by purpose and origin
