# Example: Usage Tracking

Track token usage by purpose (main, planning, tool loop, critic, refiner) and origin (user vs framework).

## Basic usage

```python
import asyncio
from nucleusiq.agents import Agent
from nucleusiq.agents.config import AgentConfig, ExecutionMode
from nucleusiq.prompts.zero_shot import ZeroShotPrompt
from nucleusiq.tools.decorators import tool
from nucleusiq_openai import BaseOpenAI

@tool
def lookup(query: str) -> str:
    """Look up information."""
    return f"Result for: {query}"

async def main():
    agent = Agent(
        name="assistant",
        prompt=ZeroShotPrompt().configure(
            system="Use tools when needed.",
        ),
        llm=BaseOpenAI(model_name="gpt-4.1-mini"),
        tools=[lookup],
        config=AgentConfig(execution_mode=ExecutionMode.STANDARD),
    )

    result = await agent.execute(
        {"id": "u1", "objective": "Look up the population of Tokyo and explain the trend"}
    )

    # Human-readable summary
    usage = agent.last_usage
    print(usage.display())

asyncio.run(main())
```

Output:

```
Usage Summary:
  Total: 450 tokens (prompt: 280, completion: 170)
  Calls: 3

  By Purpose:
    main:      280 tokens (1 call)
    tool_loop: 170 tokens (2 calls)

  By Origin:
    user:      280 tokens (62%)
    framework: 170 tokens (38%)
```

## Programmatic access

```python
usage = agent.last_usage

# Totals
print(f"Total tokens: {usage.total.total_tokens}")
print(f"Prompt: {usage.total.prompt_tokens}")
print(f"Completion: {usage.total.completion_tokens}")
print(f"LLM calls: {usage.call_count}")

# By purpose
for purpose, bucket in usage.by_purpose.items():
    print(f"  {purpose}: {bucket.total_tokens} tokens, {bucket.call_count} calls")

# By origin (user vs framework overhead)
user = usage.by_origin.get("user")
framework = usage.by_origin.get("framework")
if user and framework:
    total = user.total_tokens + framework.total_tokens
    print(f"User: {user.total_tokens} ({user.total_tokens/total*100:.0f}%)")
    print(f"Framework: {framework.total_tokens} ({framework.total_tokens/total*100:.0f}%)")

# Dict for logging/dashboards
log_payload = usage.summary()
```

## Combined with cost estimation

```python
from nucleusiq.agents.usage import CostTracker

tracker = CostTracker()
cost = tracker.estimate(usage, model="gpt-4o-mini")
print(f"Estimated cost: ${cost.total_cost:.6f}")
```

## See also

- [Usage tracking reference](../usage-tracking.md) — Full schema documentation
- [Cost estimation](../observability/cost-estimation.md) — Dollar cost tracking
- [Cost estimation example](cost-estimation.md) — CostTracker usage
