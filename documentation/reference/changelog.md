# Changelog

All notable changes to NucleusIQ are documented in the [CHANGELOG.md](https://github.com/nucleusbox/NucleusIQ/blob/main/CHANGELOG.md) in the repository root.

## Recent releases

- **[0.7.7](https://github.com/nucleusbox/NucleusIQ/blob/main/CHANGELOG.md#077)** — Context Management v2 stability, idempotent tool opt-in, AgentResult / synthesis fixes, provider sync (OpenAI 0.6.3, Gemini 0.2.5)
- **[0.7.6](https://github.com/nucleusbox/NucleusIQ/blob/main/CHANGELOG.md#076)** — Context window management, prompt system refactor, synthesis pass, ObservabilityConfig
- **[0.7.5](https://github.com/nucleusbox/NucleusIQ/blob/main/CHANGELOG.md#075)** — Gemini native + custom tool mixing (proxy pattern), full observability wiring
- **[0.7.4](https://github.com/nucleusbox/NucleusIQ/blob/main/CHANGELOG.md#074)** — ExecutionTracer, Pyrefly type checking, error package restructure, usage extraction, exhaustive error wiring
- **[0.7.3](https://github.com/nucleusbox/NucleusIQ/blob/main/CHANGELOG.md#073)** — Gemini tool-calling fixes, `$ref`/`$defs` inlining for structured output
- **[0.7.2](https://github.com/nucleusbox/NucleusIQ/blob/main/CHANGELOG.md#072)** — Unified exception hierarchy (10 families), AgentResult response contract
- **[0.6.0](https://github.com/nucleusbox/NucleusIQ/blob/main/CHANGELOG.md#060--2026-03-13)** — Gemini provider, `@tool` decorator, cost estimation, framework error taxonomy
- **[0.5.0](https://github.com/nucleusbox/NucleusIQ/blob/main/CHANGELOG.md#050--2026-03-11)** — Token origin split, UsageSummary schema, FileWriteTool, FileExtractTool query filtering

## v0.7.7 highlights

### Packages

| Package | Version | What's new |
|---------|---------|-----------|
| `nucleusiq` | **0.7.7** | Stable Context Management v2 (single `Compactor`, bounded markers, recall/rehydration), idempotent tool metadata, clearer `AgentResult` on errors and tool-cap exhaustion |
| `nucleusiq-openai` | **0.6.3** | Sync with v0.7.7 core message/tool contracts |
| `nucleusiq-gemini` | **0.2.5** | Sync with v0.7.7 core message/tool contracts |

### Context Management v2

- One compaction pipeline, bounded observation markers, recallable offload, synthesis-time rehydration.
- Default `ContextConfig.squeeze_threshold=0.70` kept after validation on PDF-heavy runs.
- **Fixed:** rehydration uses the engine’s resolved model context window when `max_context_tokens` is auto-detected (was skipping when the field was `None`).

### Tools

- **Opt-in idempotent tools:** `BaseTool.idempotent` and `@tool(idempotent=True)`. Default remains `False` so live-data tools are never deduplicated unless you declare them safe. Identical `(tool_name, args)` short-circuits to the prior result.

### Agent execution & results

- **`AgentResult`:** legacy mode error-string outcomes surface as `status=error` when agent state is already `ERROR`, including stable `ToolCallLimitError` when the tool budget is exhausted.
- **Standard mode:** when the configured tool-call cap is reached and synthesis is enabled, the runtime forces a **tools-free synthesis** pass so autonomous flows can still reach validation/refinement instead of stopping on a raw limit string.

### Telemetry

- Compaction telemetry distinguishes **tokens freed by the observation masker** vs **by compactors** (finer-grained than a single `tokens_freed` where applicable).

### Autonomous mode

- **Critic / Refiner** wired with context helpers (e.g. `extract_raw_trace` from `ContentStore`) so critique passes can work from masked traces where appropriate.

### Tests & validation

- Broad recall/masking tests (policy, squeeze gating, markers, synthesis rehydration, streaming vs non-streaming symmetry).
- Autonomous stability tests (critic/refiner routing, abstention, compute-budget escalation, tool-budget synthesis).

See the full [CHANGELOG.md on GitHub](https://github.com/nucleusbox/NucleusIQ/blob/main/CHANGELOG.md#077--2026-04-27) for known limitations and CI notes.

## v0.7.6 highlights

### Packages

| Package | Version | What's new |
|---------|---------|-----------|
| `nucleusiq` | **0.7.6** | Context window management, prompt system refactor, synthesis pass, ObservabilityConfig |
| `nucleusiq-openai` | **0.6.2** | Context window registry (20 models), `get_context_window()`, prompt API migration |
| `nucleusiq-gemini` | **0.2.4** | `get_context_window()` method override, prompt API migration |

### Context Window Management

Automatic context management for tool-heavy agents. Prevents context overflow when agents make many tool calls, ensuring the LLM always has room to respond.

Key additions: `ContextConfig`, `ContextEngine`, `ContextStrategy` enum, `ContextTelemetry`.

See [Context management guide](../python/nucleusiq/context-management.md).

### Prompt System Refactor (Breaking)

- `prompt` is now **mandatory** on `Agent` (was `Optional[BasePrompt]`)
- `narrative` field **removed** — move content to `prompt.system`
- `role` and `objective` are **labels only** — not sent to the LLM
- `ZeroShotPrompt` — only `system` is required; `user` is optional

See [Migration notes](../python/nucleusiq/learn/migration-notes.md#from-v075-to-v076).

### Synthesis Pass

After multi-round tool loops, the agent makes one final LLM call without tools to produce the full deliverable. Breaks the "mode inertia" problem. Controlled by `AgentConfig(enable_synthesis=True)` (default).

### ObservabilityConfig

Unified config replacing `verbose` + `enable_tracing`: `tracing`, `verbose`, `log_level`, `log_llm_calls`, `log_tool_results`. Backward compatible with legacy fields.

### Provider Updates

- **OpenAI** — new `_CONTEXT_WINDOWS` registry with 20 models, `get_context_window()` method
- **Gemini** — `get_context_window()` method wired to existing `_MODEL_REGISTRY`

### Tests

- 97 new context management unit tests + 4 agent-level integration tests
- 27 existing test files updated for prompt system refactor
- For current test counts and gates, see the [upstream CHANGELOG](https://github.com/nucleusbox/NucleusIQ/blob/main/CHANGELOG.md) for the release you are on (v0.7.7 focused gates: ~1,340+ on context/agent slices; full suite ~2,469+ with skips per environment).

## v0.7.5 highlights

### Packages

| Package | Version | What's new |
|---------|---------|-----------|
| `nucleusiq` | 0.7.5 | Full observability wiring — PluginEvent, MemorySnapshot, AutonomousDetail tracing |
| `nucleusiq-openai` | 0.6.1 | No changes |
| `nucleusiq-gemini` | 0.2.3 | Native + custom tool mixing via transparent proxy pattern |

### Part A: Gemini Native + Custom Tool Mixing

Google's Gemini 2.5 API rejects requests that mix native tools (`google_search`, `code_execution`, `url_context`, `google_maps`) with custom function declarations. NucleusIQ v0.7.5 resolves this transparently with a **proxy pattern** — entirely within the Gemini provider, zero core framework changes.

See [Gemini provider guide — Mixing native and custom tools](../python/nucleusiq/guides/gemini-provider.md#mixing-native-and-custom-tools).

### Part B: Full Observability Wiring

`AgentResult` now captures every dimension of an execution when `enable_tracing=True`:

| New field | What it captures |
|-----------|-----------------|
| `result.plugin_events` | Every plugin hook fired — name, duration, payload |
| `result.memory_snapshot` | Conversation messages and token count at execution end |
| `result.autonomous` | Decomposition steps, sub-task names, validation records, critic scores |
| `result.llm_calls[].prompt_technique` | Which prompt strategy was used (e.g. `chain_of_thought`) |

See [Observability docs](../python/nucleusiq/observability/index.md).

## v0.7.4 highlights

- **ExecutionTracer observability** — full LLM/tool call tracing
- **AgentResult response contract** — typed, immutable Pydantic model (v0.7.2)
- **Full exception hierarchy** — 10 error families (v0.7.2)
- **Gemini tool-calling fixes** (v0.7.3)
- **Pyrefly type checking** — 121 type errors fixed, CI-gated
- **Architecture cleanup** — `core/errors/` and `core/agents/usage/` packages

For the full history, see [CHANGELOG.md](https://github.com/nucleusbox/NucleusIQ/blob/main/CHANGELOG.md) on GitHub.
