# Observability

Track and optimize runtime behavior, token usage, costs, and context management.

NucleusIQ provides built-in observability primitives that let you inspect what happened during an agent execution — every LLM call, every tool invocation, token counts, estimated dollar costs, and context window management metrics.

## ObservabilityConfig

*New in v0.7.6*

Unified observability configuration that replaces the separate `verbose` and `enable_tracing` fields:

```python
from nucleusiq.agents import Agent
from nucleusiq.agents.config import AgentConfig, ExecutionMode
from nucleusiq.agents.config.observability_config import ObservabilityConfig
from nucleusiq.prompts.zero_shot import ZeroShotPrompt
from nucleusiq_openai import BaseOpenAI

agent = Agent(
    name="analyst",
    prompt=ZeroShotPrompt().configure(
        system="You are a data analyst.",
    ),
    llm=BaseOpenAI(model_name="gpt-4.1-mini"),
    config=AgentConfig(
        execution_mode=ExecutionMode.STANDARD,
        observability=ObservabilityConfig(
            tracing=True,
            verbose=True,
            log_level="DEBUG",
            log_llm_calls=True,
            log_tool_results=True,
        ),
    ),
)
```

| Field | Default | Description |
|-------|---------|-------------|
| `tracing` | `False` | Enable execution tracing (populates `AgentResult.tool_calls`, `.llm_calls`) |
| `verbose` | `False` | Enable debug-level logging |
| `log_level` | `"INFO"` | Logger level string |
| `log_llm_calls` | `False` | Log detailed LLM call info |
| `log_tool_results` | `False` | Log tool execution results |

When `observability` is set on `AgentConfig`, it takes precedence over the legacy `verbose` and `enable_tracing` fields. Both approaches are backward compatible — use whichever you prefer.

### Legacy approach (still works)

```python
config = AgentConfig(
    enable_tracing=True,
    verbose=True,
)
```

## ExecutionTracer

*New in v0.7.4*

`ExecutionTracer` records every LLM call and tool call that occurs during an agent execution. Enable it via `AgentConfig`:

```python
import asyncio
from nucleusiq.agents import Agent
from nucleusiq.agents.config import AgentConfig, ExecutionMode
from nucleusiq.prompts.zero_shot import ZeroShotPrompt
from nucleusiq.tools.decorators import tool
from nucleusiq_openai import BaseOpenAI

@tool
def search(query: str) -> str:
    """Search for information."""
    return f"Results for: {query}"

async def main():
    agent = Agent(
        name="analyst",
        prompt=ZeroShotPrompt().configure(
            system="You are a research analyst. Use tools to gather data.",
        ),
        llm=BaseOpenAI(model_name="gpt-4.1-mini"),
        tools=[search],
        config=AgentConfig(
            execution_mode=ExecutionMode.STANDARD,
            enable_tracing=True,
        ),
    )
    result = await agent.execute({"id": "o1", "objective": "Research AI trends"})

    # Inspect traced tool calls
    for tc in result.tool_calls:
        print(f"Tool: {tc['name']}, Duration: {tc['duration_ms']}ms")

    # Inspect traced LLM calls
    for lc in result.llm_calls:
        print(f"LLM call: {lc['purpose']}, Tokens: {lc['usage']}")
        print(f"Prompt technique: {lc.get('prompt_technique', 'n/a')}")  # v0.7.6

    # Warnings
    for w in result.warnings:
        print(f"Warning: {w}")

asyncio.run(main())
```

The trace captures:

| Field | Type | Description |
|-------|------|-------------|
| `result.tool_calls` | `tuple[dict, ...]` | Tool invocations with name, arguments, duration, and return value |
| `result.llm_calls` | `tuple[dict, ...]` | LLM calls with purpose, model, token usage, latency, and prompt technique |
| `result.warnings` | `tuple[str, ...]` | Warnings emitted during execution (e.g. retries, fallback behavior) |

### Full observability wiring (v0.7.5)

With tracing enabled, `AgentResult` now captures the **complete execution picture**:

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
| `result.llm_calls[].prompt_technique` | `str | None` | Which prompt strategy was used (e.g. `zero_shot`) |

## Context Telemetry

*New in v0.7.6*

When context management is configured, `AgentResult` includes a `context_telemetry` field:

```python
tel = result.context_telemetry
if tel:
    print(f"Peak utilization: {tel.peak_utilization:.1%}")
    print(f"Tokens saved:     {tel.tokens_masked:,}")
    print(f"Estimated savings: ${tel.estimated_cost_savings:.4f}")
```

See [Context management](../context-management.md) for configuration and telemetry details.

## Run-local state metadata (v0.7.8)

Separate from **`context_telemetry`** (context window engine), **`AgentResult.metadata`** is a **`dict`** that may summarize **run-local** workspace / evidence / corpus state and activation telemetry:

```python
result = await agent.execute(task)
meta = result.metadata or {}

for key in ("workspace", "evidence", "document_search", "phase_control", "context_activation", "synthesis_package"):
    if key in meta:
        print(f"{key}: {meta[key]}")
```

| Key | Typical contents |
|-----|------------------|
| `workspace` | Stats from `InMemoryWorkspace` (entry counts, limits). |
| `evidence` | Stats from `InMemoryEvidenceDossier`. |
| `document_search` | `DocumentSearchStats` — chunks indexed, searches, promotions to evidence. |
| `phase_control` | Phase durations, evidence-gate outcome, flags (`synthesis_used_package`, `critic_used_package`, …). |
| `context_activation` | `ContextActivationMetrics` counters from **`ContextStateActivator`**. |
| `synthesis_package` | Metadata dict from the last **`SynthesisPackage`** built during the run (if any). |

Details: [Run-local context state](../run-local-context-state.md).

### Display

`AgentResult.display()` renders a human-readable summary including all traced fields:

```python
result.display()
```

```
--- AgentResult ---
Status:   success
Duration: 31,452 ms
Output:   The temperature in Tokyo is 15C (59F)...
LLM calls (6):
  [main      ] gpt-4.1-mini  4,879ms  tokens_in=473 tokens_out=18
  [tool_loop ] gpt-4.1-mini  4,505ms  tokens_in=562 tokens_out=32
  [synthesis ] gpt-4.1-mini  8,231ms  tokens_in=1204 tokens_out=2048
  ...
Tool calls (5):
  Round 1: google_search        success=True  3,306ms
  Round 2: unit_converter       success=True  0.1ms
  ...
Context:
  Peak utilization: 67.2%
  Observations masked: 5
  Tokens saved: 12,450
```

## Usage tracking

Token usage is tracked automatically on every execution — no configuration needed. Access aggregated counts — broken down by purpose (main, planning, tool loop, critic, refiner, synthesis) and origin (user vs framework) — via `agent.last_usage`.

```python
result = await agent.execute(task)

usage = agent.last_usage
print(usage.display())

# Programmatic access
print(f"Total tokens: {usage.total.total_tokens}")
print(f"LLM calls: {usage.call_count}")

# By purpose
for purpose, bucket in usage.by_purpose.items():
    print(f"  {purpose}: {bucket.total_tokens} tokens, {bucket.call_count} calls")

# Export for logging/dashboards
log_payload = usage.summary()
```

See [Usage tracking](../usage-tracking.md) for the full schema, programmatic access, and logging examples.

## Cost estimation

Convert token usage into dollar costs using the built-in `CostTracker`, which ships with pricing tables for OpenAI and Gemini models.

```python
from nucleusiq.agents.usage import CostTracker

tracker = CostTracker()
cost = tracker.estimate(agent.last_usage, model="gpt-4.1-mini")
print(f"Estimated cost: ${cost.total_cost:.6f}")
print(f"  Prompt:     ${cost.prompt_cost:.6f}")
print(f"  Completion: ${cost.completion_cost:.6f}")
print(cost.display())
```

See [Cost estimation](cost-estimation.md) for built-in pricing tables, custom model registration, and prefix matching.

## Zero overhead by default

Tracing is **off** by default. When `enable_tracing` is not set (or set to `False`), `result.tool_calls`, `result.llm_calls`, and `result.warnings` are empty tuples — no runtime overhead. Usage tracking (`agent.last_usage`) is always available regardless of tracing.

## See also

- [Context management](../context-management.md) — Context window management guide
- [Usage tracking](../usage-tracking.md) — Token usage by purpose and origin
- [Cost estimation](cost-estimation.md) — Dollar cost tracking with built-in pricing tables
- [Agent Config guide](../guides/agent-config.md) — ObservabilityConfig configuration
