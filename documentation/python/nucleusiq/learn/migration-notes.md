# Migration notes

## From v0.7.5 to v0.7.6

v0.7.6 includes **breaking changes** to the prompt system and adds context window management.

### Breaking changes

| Change | Migration |
|--------|----------|
| `prompt` is now **mandatory** on `Agent` | Add `prompt=ZeroShotPrompt().configure(system="...")` to all agent constructors. |
| `narrative` field **removed** | Move content from `narrative=` to `prompt.system`. |
| `role` and `objective` are **labels only** | They are no longer sent to the LLM. Move any LLM instructions to `prompt.system`. |
| `MessageBuilder.build()` no longer accepts `role`, `objective`, `narrative` | If you call `MessageBuilder` directly, pass `prompt=` instead. |
| `ZeroShotPrompt` — `user` is now optional | Only `system` is required. The task objective provides the user query. |

### Before / After

**Agent creation:**

```python
# BEFORE (v0.7.5) — narrative was silently ignored, role/objective built the system message
agent = Agent(
    name="MyBot",
    role="Analyst",
    objective="Analyze data",
    narrative="You are a data analyst. Provide detailed analysis.",
    llm=llm,
)

# AFTER (v0.7.6) — prompt is mandatory and is the single source of truth
from nucleusiq.prompts.zero_shot import ZeroShotPrompt

agent = Agent(
    name="MyBot",
    role="Analyst",              # label only — NOT sent to LLM
    objective="Analyze data",    # label only — NOT sent to LLM
    prompt=ZeroShotPrompt().configure(
        system="You are a data analyst. Provide detailed analysis.",
    ),
    llm=llm,
)
```

**With tools and context management (new in v0.7.6):**

```python
# AFTER (v0.7.6) — full agent with context management
from nucleusiq.agents import Agent
from nucleusiq.agents.config import AgentConfig, ExecutionMode
from nucleusiq.agents.context import ContextConfig, ContextStrategy
from nucleusiq.prompts.zero_shot import ZeroShotPrompt
from nucleusiq_openai import BaseOpenAI

agent = Agent(
    name="researcher",
    prompt=ZeroShotPrompt().configure(
        system="You are a research analyst. Gather data, then write a comprehensive report.",
        user="Use all available tools to gather data before writing.",
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

result = await agent.execute({"id": "t1", "objective": "Analyze annual report"})
print(result.output)

# New: context telemetry
if result.context_telemetry:
    print(f"Peak utilization: {result.context_telemetry.peak_utilization:.1%}")
```

**MessageBuilder (if you use it directly):**

```python
# BEFORE (v0.7.5)
messages = MessageBuilder.build(
    role="Analyst",
    objective="Analyze data",
    narrative="You are a data analyst.",
    memory_messages=memory_messages,
)

# AFTER (v0.7.6)
from nucleusiq.prompts.zero_shot import ZeroShotPrompt

prompt = ZeroShotPrompt().configure(system="You are a data analyst.")
messages = MessageBuilder.build(
    prompt=prompt,
    memory_messages=memory_messages,
)
```

### New features (non-breaking)

| Feature | What to do |
|---------|-----------|
| Context window management | Add `context=ContextConfig(...)` to `AgentConfig` for tool-heavy agents. Optional — no context management applied if omitted. |
| Synthesis pass | Enabled by default (`enable_synthesis=True`). Set `False` to disable. |
| `ObservabilityConfig` | Optional replacement for `verbose` + `enable_tracing`. Backward compatible. |
| `ContextStrategy` enum | Use `ContextStrategy.PROGRESSIVE`, `.TRUNCATE_ONLY`, or `.NONE`. |
| Context telemetry | `result.context_telemetry` available when context management is configured. |

### Package versions

| Package | Version | Requires |
|---------|---------|----------|
| `nucleusiq` | **0.7.7** (current) | — |
| `nucleusiq-openai` | **0.6.3** | `nucleusiq>=0.7.7` |
| `nucleusiq-gemini` | **0.2.5** | `nucleusiq>=0.7.7` |

Upgrade all three:

```bash
pip install --upgrade nucleusiq nucleusiq-openai nucleusiq-gemini
```

If you must stay on v0.7.6 for a short period, use `nucleusiq==0.7.6` with `nucleusiq-openai==0.6.2` and `nucleusiq-gemini==0.2.4`.

## From v0.7.6 to v0.7.7

v0.7.7 is **backward compatible** for typical agent code. No prompt or `Agent` constructor changes are required beyond staying on the v0.7.6 API (`prompt` mandatory, etc.).

### What changed (behavior you may notice)

| Area | Change |
|------|--------|
| **Context V2** | Stabilized compaction/masking pipeline; default `squeeze_threshold` remains **0.70**. Rehydration after masking now respects auto-detected model context windows. |
| **Tool budgets** | When `max_tool_calls` is **not** set, mode defaults are **25 / 80 / 300** (Direct / Standard / Autonomous) — higher than the early **5 / 30 / 100** values. Set `max_tool_calls` explicitly if you need a lower cap. Same value limits **tool invocations per run** and how many **user-registered** tools the agent may carry (framework recall tools excluded). |
| **Tools** | Optional **`idempotent=True`** on `@tool` / `BaseTool` — identical `(name, args)` replays can short-circuit. **Default is still `False`** (safe for APIs, DB, time-dependent tools). |
| **`AgentResult`** | Error paths and exhausted **tool-call limits** map to **`status=error`** (and `ToolCallLimitError` where applicable) instead of looking like success with a bare error string. |
| **Standard + synthesis** | When the **tool cap** is hit and **`enable_synthesis`** is on, the runtime runs a **final tools-off synthesis** so downstream autonomous validation can still run. |
| **Telemetry** | Finer breakdown of **tokens freed** (masker vs compactor) in compaction-related telemetry where exposed. |
| **Autonomous** | Critic/Refiner paths use **`extract_raw_trace`**-style rehydration from the content store when working from masked traces. |

### Optional: mark a tool idempotent

```python
from nucleusiq.tools.decorators import tool

@tool(idempotent=True)
def list_allowed_urls() -> str:
    """Static catalog — same args always same result."""
    return "https://a.example,https://b.example"
```

See [@tool decorator](../tools/tool-decorator.md#idempotent-tools-same-args-same-result).

## From v0.7.4 to v0.7.5

Key changes in v0.7.5:

| Change | Migration |
|--------|----------|
| Gemini native + custom tool mixing works transparently | No code changes needed. If you were working around the 400 error (separate agents, avoiding native tools), you can now simply pass all tools to a single agent. |
| `AgentResult` has new tracing fields | `result.plugin_events`, `result.memory_snapshot`, `result.autonomous` are available when `enable_tracing=True`. Empty/`None` when tracing is off — no breaking change. |
| `AgentResult.display()` enhanced | Shows plugin events, memory snapshot, and autonomous detail sections. Informational only. |
| `nucleusiq-gemini` 0.2.3 | Upgrade: `pip install --upgrade nucleusiq-gemini`. Contains `tool_splitter.py` and proxy mode. |
| `LLMCallRecord.prompt_technique` field | New optional field. Existing code unaffected. |

## From v0.6.0 to v0.7.x

Key changes in v0.7.x:

| Change | Migration |
|--------|----------|
| `agent.execute()` returns `AgentResult` not raw string | Use `result.output` for text, `str(result)` for string, `result.status` for outcome |
| New exception hierarchy | Replace `except ValueError` with `except ToolValidationError`, `except AgentExecutionError`, etc. |
| `from nucleusiq.agents.components.pricing import CostTracker` moved | Use `from nucleusiq.agents.usage import CostTracker` |
| `from nucleusiq.agents.components.usage_tracker import UsageTracker` moved | Use `from nucleusiq.agents.usage import UsageTracker` |
| `AgentConfig.enable_tracing` new field | Set `enable_tracing=True` to populate `AgentResult.tool_calls`, `.llm_calls`, `.warnings` |
| All errors now have structured attributes | `ToolError` carries `tool_name`, `AgentError` carries `mode`, etc. |

## From simpler chat wrappers

If you are migrating from direct API calls or thin wrappers:

1. Move from `prompt -> response` to `Agent + execute()`
2. Create a `ZeroShotPrompt().configure(system="...")` for your LLM instructions
3. Introduce tools gradually using the `@tool` decorator in STANDARD mode
4. Add memory with `MemoryFactory.create_memory(MemoryStrategy.SLIDING_WINDOW)`
5. Use `agent.last_usage` and `CostTracker` to monitor costs
6. Add plugins for guardrails: `ModelCallLimitPlugin`, `ToolGuardPlugin`

## From heavier workflow systems (LangChain, etc.)

If you are migrating from a heavier framework:

1. Start with one Agent + STANDARD mode — NucleusIQ's single-agent model covers most cases
2. Replace chain/graph abstractions with execution modes (Direct -> Standard -> Autonomous)
3. Add plugins for policy and retries instead of custom middleware
4. Introduce AUTONOMOUS mode only where Critic/Refiner verification loops are genuinely needed
5. Use provider portability to switch LLMs without rewriting agent logic

## From v0.5.0 to v0.6.0

Key changes in v0.6.0:

| Change | Migration |
|--------|----------|
| `max_tokens` -> `max_output_tokens` | Update `AgentConfig` and `LLMParams` usages |
| `nucleusiq-openai` now requires `nucleusiq>=0.6.0` | Upgrade core first: `pip install --upgrade nucleusiq` |
| New error types in `nucleusiq.llms.errors` | Replace bare `except Exception` with specific error catches |
| `@tool` decorator available | Optional — existing `BaseTool` subclasses still work |
| `CostTracker` available | Optional add-on for cost monitoring |

## See also

- [Changelog](../../../reference/changelog.md) — Full release history
- [Production path](production-path.md) — Production readiness checklist
