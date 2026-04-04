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

### Full observability wiring (v0.7.5)

*New in v0.7.5*

With tracing enabled, `AgentResult` now captures the **complete execution picture** — not just LLM and tool calls, but plugin activity, memory state, and autonomous orchestration details:

```python
result = await agent.execute(task)

# Plugin events — every hook with timing
for pe in result.plugin_events:
    print(f"Plugin: {pe.hook_name}, Duration: {pe.duration_ms:.1f}ms")

# Memory snapshot — conversation state at execution end
if result.memory_snapshot:
    print(f"Messages: {result.memory_snapshot.message_count}")
    print(f"Tokens: {result.memory_snapshot.token_count}")

# Autonomous detail (only in AUTONOMOUS mode)
if result.autonomous:
    print(f"Sub-tasks: {result.autonomous.sub_task_names}")
    for v in result.autonomous.validations:
        print(f"  Validation: score={v.score}, passed={v.passed}")
```

| Field | Type | Description |
|-------|------|-------------|
| `result.plugin_events` | `tuple[PluginEvent, ...]` | Every plugin hook fired — hook name, duration, and payload |
| `result.memory_snapshot` | `MemorySnapshot | None` | Conversation messages and token count at execution end |
| `result.autonomous` | `AutonomousDetail | None` | Decomposition, sub-task names, validation records, critic scores |
| `result.llm_calls[].prompt_technique` | `str | None` | Which prompt strategy was used (e.g. `chain_of_thought`) |

**What was previously invisible and is now traced:**

- **Plugin hooks** — `PluginManager` records timing for all 6 hooks (`before_llm_call`, `after_llm_call`, `before_tool_call`, `after_tool_call`, `before_execution`, `after_execution`)
- **Decomposer LLM call** — `Decomposer.analyze()` makes a direct LLM call that bypassed the tracer; now manually recorded
- **Memory state** — captured from the agent's memory at the end of `_build_result()`
- **Autonomous validation** — critic scores and pass/fail status for each validation round

### Display

`AgentResult.display()` renders a human-readable summary including all traced fields:

```python
result.display()
```

```
--- AgentResult ---
Status:   success
Duration: 31,452 ms
Output:   The temperature in Tokyo is 15°C (59°F)...
LLM calls (6):
  [main      ] gemini-2.5-pro  4,879ms  tokens_in=473 tokens_out=18
  [tool_loop ] gemini-2.5-pro  4,505ms  tokens_in=562 tokens_out=32
  ...
Tool calls (5):
  Round 1: google_search        success=True  3,306ms
  Round 2: unit_converter       success=True  0.1ms
  ...
Plugin events (4):
  before_execution  12.3ms
  before_llm_call   0.1ms
  ...
```

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
