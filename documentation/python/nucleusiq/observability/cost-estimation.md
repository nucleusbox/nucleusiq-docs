# Cost estimation

NucleusIQ includes a `CostTracker` that estimates dollar costs from token usage data, with built-in pricing tables for OpenAI and Gemini models.

## Quick usage

```python
from nucleusiq.agents.components.pricing import CostTracker

result = await agent.execute({"id": "cost-estimation-1", "objective": "Analyze this data"})
usage = agent.last_usage

tracker = CostTracker()
cost = tracker.estimate(usage, model="gemini-2.5-flash")

print(cost.display())
```

Output:

```
Cost Breakdown (gemini-2.5-flash):
  Prompt:     $0.000045
  Completion: $0.000180
  Total:      $0.000225
```

## CostBreakdown

`tracker.estimate()` returns a `CostBreakdown` with:

| Field | Description |
|-------|-------------|
| `total_cost` | Total estimated cost (prompt + completion) |
| `prompt_cost` | Cost for input/prompt tokens |
| `completion_cost` | Cost for output/completion tokens |
| `model` | Model name used for pricing lookup |
| `by_purpose` | Cost breakdown by call purpose (main, planning, tool_loop, critic, refiner) |
| `by_origin` | Cost breakdown by origin (user vs framework) |

```python
cost = tracker.estimate(usage, model="gpt-4o")

print(f"Total: ${cost.total_cost:.6f}")
print(f"Prompt: ${cost.prompt_cost:.6f}")
print(f"Completion: ${cost.completion_cost:.6f}")

# See where your money goes
for purpose, amount in cost.by_purpose.items():
    print(f"  {purpose}: ${amount:.6f}")
```

## Built-in pricing

Pricing tables are included for common models:

### OpenAI models

| Model | Prompt (per 1K tokens) | Completion (per 1K tokens) |
|-------|----------------------|--------------------------|
| gpt-4o | $0.0025 | $0.01 |
| gpt-4o-mini | $0.00015 | $0.0006 |
| gpt-4.1 | $0.002 | $0.008 |
| gpt-4.1-mini | $0.0004 | $0.0016 |
| gpt-4.1-nano | $0.0001 | $0.0004 |
| o3 | $0.01 | $0.04 |
| o3-mini | $0.00110 | $0.0044 |
| o4-mini | $0.00110 | $0.0044 |
| o1 | $0.015 | $0.06 |
| o1-mini | $0.003 | $0.012 |
| gpt-3.5-turbo | $0.0005 | $0.0015 |

### Gemini models

| Model | Prompt (per 1K tokens) | Completion (per 1K tokens) |
|-------|----------------------|--------------------------|
| gemini-2.5-pro | $0.00125 | $0.01 |
| gemini-2.5-flash | $0.000075 | $0.0003 |
| gemini-2.0-flash | $0.0001 | $0.0004 |
| gemini-1.5-pro | $0.00125 | $0.005 |
| gemini-1.5-flash | $0.000075 | $0.0003 |

## Custom pricing

Register pricing for custom or fine-tuned models:

```python
from nucleusiq.agents.components.pricing import CostTracker, ModelPricing

tracker = CostTracker()
tracker.register("my-fine-tuned-model", ModelPricing(
    prompt_price_per_1k=0.003,
    completion_price_per_1k=0.012,
))

cost = tracker.estimate(usage, model="my-fine-tuned-model")
```

## Prefix matching

Model names are matched by prefix, so versioned model names work automatically:

```python
# All of these match the "gpt-4o" pricing entry
tracker.estimate(usage, model="gpt-4o")
tracker.estimate(usage, model="gpt-4o-2024-11-20")
tracker.estimate(usage, model="gpt-4o-mini-custom")
```

## Integration with usage tracking

Cost estimation builds on top of [usage tracking](../usage-tracking.md):

```python
result = await agent.execute({"id": "cost-estimation-2", "objective": "Complex analysis task"})

# Token usage (always available)
usage = agent.last_usage
print(usage.display())

# Cost estimation (add-on)
tracker = CostTracker()
cost = tracker.estimate(usage, model="gpt-4o")
print(cost.display())

# Drill into framework overhead cost
framework_cost = cost.by_origin.get("framework", 0)
user_cost = cost.by_origin.get("user", 0)
print(f"User cost: ${user_cost:.6f}, Framework overhead: ${framework_cost:.6f}")
```

## See also

- [Usage tracking](../usage-tracking.md) — Token usage by purpose and origin
- [Models](../models.md) — Supported models and providers
