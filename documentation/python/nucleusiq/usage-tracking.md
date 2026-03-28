# Usage tracking

NucleusIQ tracks token usage for each execution and exposes it on `agent.last_usage`.

## Quick usage

```python
result = await agent.execute(task)

# Human-readable summary for console/debug
print(agent.last_usage.display())

# Plain dict for logs, telemetry, dashboards
usage_dict = agent.last_usage.summary()
```

## UsageSummary schema

`agent.last_usage` is a typed `UsageSummary` model with:

- `total` — aggregated token counts (`prompt_tokens`, `completion_tokens`, `reasoning_tokens`, `total_tokens`)
- `call_count` — number of LLM calls in the execution
- `by_purpose` — token/call breakdown by call purpose
- `by_origin` — user vs framework token split

## by_purpose breakdown

Purposes tracked by the runtime:

- `main` — primary call for user objective
- `planning` — autonomous planning calls
- `tool_loop` — follow-up calls after tool outputs
- `critic` — verification calls
- `refiner` — correction/refinement calls

## by_origin breakdown

Origins are coarse attribution buckets:

- `user` — the initial MAIN call carrying the user objective
- `framework` — orchestration overhead (planning, tool loops, critic/refiner, etc.)

```python
usage = agent.last_usage
user_tokens = usage.by_origin["user"].total_tokens
framework_tokens = usage.by_origin["framework"].total_tokens
```

## Logging example

```python
usage = agent.last_usage
framework_bucket = usage.by_origin.get("framework")

log_payload = {
    "total_tokens": usage.total.total_tokens,
    "prompt_tokens": usage.total.prompt_tokens,
    "completion_tokens": usage.total.completion_tokens,
    "framework_tokens": framework_bucket.total_tokens if framework_bucket else 0,
}
print(log_payload)
```

## Mode interpretation

- **DIRECT** usually has the lowest framework overhead.
- **STANDARD** adds overhead from tool loops when tools are used.
- **AUTONOMOUS** typically has higher framework overhead due to planning and validation cycles.

Use this data to tune mode selection, tool strategy, and LLM settings for cost/performance balance.

## Cost estimation

Convert token usage into dollar costs using the built-in `CostTracker`:

```python
from nucleusiq.agents.components.pricing import CostTracker

tracker = CostTracker()
cost = tracker.estimate(agent.last_usage, model="gpt-4o")
print(cost.display())
```

See [Cost estimation](observability/cost-estimation.md) for full details, built-in pricing tables, and custom model registration.

## See also

- [Cost estimation](observability/cost-estimation.md) — Dollar cost tracking
- [Agents](agents.md) — Lifecycle and execution entry points
- [Execution modes](execution-modes.md) — Direct vs Standard vs Autonomous behavior
- [Models](models.md) — LLM config and per-task parameter overrides
