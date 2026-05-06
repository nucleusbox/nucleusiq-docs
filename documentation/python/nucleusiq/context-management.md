# Context Window Management

*Introduced in v0.7.6; stabilized in v0.7.7 (Context Management v2); complemented in **v0.7.8** by run-local workspace/evidence/corpus state (separate from transcript compaction).*

Tool-heavy agents can fill the context window, leaving no room for the LLM's final response. NucleusIQ automatically tracks and compacts context to keep it within budget.

**Doc numbering:** transcript hygiene (**masking + compaction**) is **L0–L3** in [Context stack layers (L0–L7)](context-stack-layers.md); **run-local workspace/evidence/corpus** is **L4–L6** on that same map.

## Quick Start

```python
from nucleusiq.agents import Agent
from nucleusiq.agents.config import AgentConfig, ExecutionMode
from nucleusiq.agents.context import ContextConfig, ContextStrategy
from nucleusiq.prompts.zero_shot import ZeroShotPrompt
from nucleusiq.tools.builtin import FileReadTool, FileSearchTool
from nucleusiq_openai import BaseOpenAI

agent = Agent(
    name="researcher",
    prompt=ZeroShotPrompt().configure(
        system="You are a research analyst. Gather data, then write a report.",
    ),
    llm=BaseOpenAI(model_name="gpt-4.1-mini", timeout=120.0),
    tools=[
        FileReadTool(workspace_root="./workspace"),
        FileSearchTool(workspace_root="./workspace"),
    ],
    config=AgentConfig(
        execution_mode=ExecutionMode.STANDARD,
        context=ContextConfig(
            optimal_budget=50_000,
            strategy=ContextStrategy.PROGRESSIVE,
        ),
    ),
)

result = await agent.execute({"id": "t1", "objective": "Analyze the annual report"})
print(result.output)

# Context telemetry
if result.context_telemetry:
    tel = result.context_telemetry
    print(f"Peak utilization: {tel.peak_utilization:.1%}")
    print(f"Tokens saved:     {tel.tokens_masked:,}")
```

## ContextConfig

| Field | Default | Description |
|-------|---------|-------------|
| `optimal_budget` | `50_000` | Target token budget |
| `strategy` | `ContextStrategy.PROGRESSIVE` | Compaction strategy |
| `enable_observation_masking` | `True` | Strip consumed tool results after each LLM response |
| `cost_per_million_input` | `0.0` | For cost-savings telemetry (e.g. `0.40` for GPT-4.1-mini) |

### Mode-aware defaults

```python
config = ContextConfig.for_mode("autonomous")  # optimal_budget=40_000
config = ContextConfig.for_mode("standard")     # optimal_budget=50_000
```

## ContextStrategy

| Strategy | Enum | Description |
|----------|------|-------------|
| Progressive | `ContextStrategy.PROGRESSIVE` | Recommended — full compaction pipeline |
| Truncate only | `ContextStrategy.TRUNCATE_ONLY` | Simple truncation, no offloading |
| None | `ContextStrategy.NONE` | Disabled entirely |

## Synthesis Pass

After multi-round tool loops, the agent makes one final LLM call without tools to produce the complete deliverable. Enabled by default.

```python
config = AgentConfig(enable_synthesis=True)  # default
```

## ContextTelemetry

Available on `AgentResult` when context management is configured:

```python
tel = result.context_telemetry
if tel:
    print(f"Peak utilization:    {tel.peak_utilization:.1%}")
    print(f"Final utilization:   {tel.final_utilization:.1%}")
    print(f"Observations masked: {tel.observations_masked}")
    print(f"Tokens masked:       {tel.tokens_masked:,}")
    print(f"Estimated savings:   ${tel.estimated_cost_savings:.4f}")
```

## Without ContextConfig

If you don't pass a `ContextConfig`, no context management is applied — the agent behaves exactly as in v0.7.5.

## v0.7.7 — V2 stability notes

- **Single compaction pipeline** — masking, tool-result compaction, conversation compaction, and emergency compaction share one coherent `Compactor` story.
- **Default `squeeze_threshold`** stays **0.70** — tuned so later masking still respects hard context limits on PDF-heavy runs.
- **Markers stay small** — large tool results get a short orientation preview in markers so markers don’t become a second evidence store.
- **Rehydration** — when the model context window is **auto-detected** from the provider, synthesis-time rehydration uses that resolved window (fixes cases where `max_context_tokens` was `None` and rehydration was skipped).
- **Advanced** — for autonomous critique/refinement, the runtime may rebuild a richer trace from the `ContentStore` via **`extract_raw_trace`** (see `nucleusiq.agents.context.store` in the core package). Most users only need `ContextConfig` + `AgentResult.context_telemetry`.

**Notebooks:** `context_management_tcs_deep_dive.ipynb` and `context_window_management_showcase.ipynb` in the main repo demonstrate end-to-end behavior.

## v0.7.8 — Run-local context state (add-on)

Compaction and masking still manage **tokens in the chat transcript**. **v0.7.8** adds an optional **per-run** stack—workspace notes, an evidence dossier, a lexical text corpus (L5), automatic promotion/indexing after tool results (L4.5), and phase/evidence-gate telemetry (L6). These subsystems use **`AgentConfig`** fields such as **`evidence_gate_required_tags`** and **`context_tool_result_corpus_max_chars`**, and expose summaries under **`AgentResult.metadata`**.

For architecture, tool names, and limits, read **[Run-local context state](run-local-context-state.md)**.

## See also

- [Context stack layers (L0–L7)](context-stack-layers.md) — Unified map: L0–L3 transcript compaction, L4–L6 run-local state, L7 output closure
- [Run-local context state](run-local-context-state.md) — Workspace, evidence, corpus, activation, phase gate (v0.7.8)
- [Agent Config guide](guides/agent-config.md) — Full AgentConfig reference
- [Execution modes](execution-modes.md) — How modes work with context management
- [Observability](observability/index.md) — Telemetry in AgentResult
- [Migration notes](learn/migration-notes.md) — Upgrading across v0.7.x (prompt refactor, V2 context, run-local state)
