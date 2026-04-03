# Observability

Track and optimize runtime behavior, token usage, and costs.

NucleusIQ provides built-in observability primitives that let you inspect what happened during an agent execution — every LLM call, every tool invocation, token counts, and estimated dollar costs.

## ExecutionTracer

*New in v0.7.4*

`ExecutionTracer` records every LLM call and tool call that occurs during an agent execution. Enable it via `AgentConfig`:

```python
from nucleusiq.agents import Agent
from nucleusiq.agents.config import AgentConfig

agent = Agent(
    name="analyst",
    llm=llm,
    config=AgentConfig(enable_tracing=True),
    ...
)
result = await agent.execute(task)

# Inspect traced data
for tc in result.tool_calls:
    print(f"Tool: {tc['name']}, Duration: {tc['duration_ms']}ms")

for lc in result.llm_calls:
    print(f"LLM call: {lc['purpose']}, Tokens: {lc['usage']}")
```

The trace captures:

| Field | Description |
|-------|-------------|
| `result.tool_calls` | Sequence of tool invocations with name, arguments, duration, and return value |
| `result.llm_calls` | Sequence of LLM calls with purpose, model, token usage, and latency |
| `result.warnings` | Any warnings emitted during execution (e.g. retries, fallback behavior) |

## Usage tracking

Token usage is tracked automatically on every execution. Access aggregated counts — broken down by purpose (main, planning, tool loop, critic, refiner) and origin (user vs framework) — via `agent.last_usage`.

```python
usage = agent.last_usage
print(usage.display())          # Human-readable summary
log_payload = usage.summary()   # Dict for dashboards / telemetry
```

See [Usage tracking](../usage-tracking.md) for the full schema, programmatic access, and logging examples.

## Cost estimation

Convert token usage into dollar costs using the built-in `CostTracker`, which ships with pricing tables for OpenAI and Gemini models.

```python
from nucleusiq.agents.usage import CostTracker

tracker = CostTracker()
cost = tracker.estimate(agent.last_usage, model="gpt-4o")
print(cost.display())
```

See [Cost estimation](cost-estimation.md) for built-in pricing tables, custom model registration, and prefix matching.

## Zero overhead by default

Tracing is **off** by default. When `enable_tracing` is not set (or set to `False`), `result.tool_calls`, `result.llm_calls`, and `result.warnings` are empty tuples — no runtime overhead, no memory allocation beyond the empty containers.

## See also

- [Usage tracking](../usage-tracking.md) — Token usage by purpose and origin
- [Cost estimation](cost-estimation.md) — Dollar cost tracking with built-in pricing tables
