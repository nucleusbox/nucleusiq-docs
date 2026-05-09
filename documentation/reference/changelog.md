# Changelog

All notable changes to NucleusIQ are documented in the [CHANGELOG.md](https://github.com/nucleusbox/NucleusIQ/blob/main/CHANGELOG.md) in the repository root.

## Recent releases

- **[0.7.9](https://github.com/nucleusbox/NucleusIQ/blob/main/CHANGELOG.md#079)** — **`retry_policy`** (429 **`Retry-After`** across Groq/OpenAI/Gemini), **`nucleusiq-groq` 0.1.0b1** public beta (`strict_model_capabilities`, streaming-open parity); **`nucleusiq-openai` 0.6.4**, **`nucleusiq-gemini` 0.2.6** (`nucleusiq>=0.7.9`)
- **[0.7.8](https://github.com/nucleusbox/NucleusIQ/blob/main/CHANGELOG.md#078)** — Run-local context state (workspace, evidence, lexical corpus), L4.5 activation, phase/evidence gate, synthesis package, tool-result serialization fix, autonomous Critic/Refiner wiring; **`nucleusiq-groq` 0.1.0a1** (since superseded by **0.1.0b1**)
- **[0.7.7](https://github.com/nucleusbox/NucleusIQ/blob/main/CHANGELOG.md#077)** — Context Management v2 stability, idempotent tool opt-in, AgentResult / synthesis fixes, provider sync (OpenAI **0.6.3**, Gemini **0.2.5**)
- **[0.7.6](https://github.com/nucleusbox/NucleusIQ/blob/main/CHANGELOG.md#076)** — Context window management, prompt system refactor, synthesis pass, ObservabilityConfig
- **[0.7.5](https://github.com/nucleusbox/NucleusIQ/blob/main/CHANGELOG.md#075)** — Gemini native + custom tool mixing (proxy pattern), full observability wiring
- **[0.7.4](https://github.com/nucleusbox/NucleusIQ/blob/main/CHANGELOG.md#074)** — ExecutionTracer, Pyrefly type checking, error package restructure, usage extraction, exhaustive error wiring
- **[0.7.3](https://github.com/nucleusbox/NucleusIQ/blob/main/CHANGELOG.md#073)** — Gemini tool-calling fixes, `$ref`/`$defs` inlining for structured output
- **[0.7.2](https://github.com/nucleusbox/NucleusIQ/blob/main/CHANGELOG.md#072)** — Unified exception hierarchy (10 families), AgentResult response contract
- **[0.6.0](https://github.com/nucleusbox/NucleusIQ/blob/main/CHANGELOG.md#060--2026-03-13)** — Gemini provider, `@tool` decorator, cost estimation, framework error taxonomy
- **[0.5.0](https://github.com/nucleusbox/NucleusIQ/blob/main/CHANGELOG.md#050--2026-03-11)** — Token origin split, UsageSummary schema, FileWriteTool, FileExtractTool query filtering

## v0.7.9 highlights — 2026-05-07

### Packages

| Package | Version | What's new |
|---------|---------|-----------|
| `nucleusiq` | **0.7.9** | **`nucleusiq.llms.retry_policy`** — shared **429** / **`Retry-After`** parsing, backoff merge, **`DEFAULT_RATE_LIMIT_MAX_SLEEP_SECONDS`** ceiling |
| `nucleusiq-openai` | **0.6.4** | Align with **`retry_policy`**; **`404`/`409`** mapped before generic **`APIError`** retry loops (`ModelNotFoundError`, **`InvalidRequestError`**) |
| `nucleusiq-gemini` | **0.2.6** | **429** honors **`Retry-After`** via **`retry_policy`**; **`nucleusiq>=0.7.9`** |
| `nucleusiq-groq` | **0.1.0b1** | Public **beta**; **`nucleusiq>=0.7.9`**; **`GroqLLMParams(strict_model_capabilities=…)`**; **`nucleusiq_groq.capabilities`**; streaming session **open** shares chat **429** policy |

### Groq provider (beta)

- **`strict_model_capabilities`** — optional gate **`parallel_tool_calls=True`** against **`PARALLEL_TOOL_CALLS_DOCUMENTED_MODELS`**.
- Stream **`open_streaming_completion`** path wired through **`stream_create`** for parity with non-stream retry semantics.

### Documentation

- **[Groq quickstart](../python/nucleusiq/examples/groq-quickstart.md)** — runnable DIRECT / STANDARD / AUTONOMOUS snippets (**beta** pins).
- **[Groq provider](../python/nucleusiq/guides/groq-provider.md)** — refreshed for beta + **`retry_policy`** narrative.

See the full [CHANGELOG.md on GitHub](https://github.com/nucleusbox/NucleusIQ/blob/main/CHANGELOG.md#079--2026-05-07) for CI gates and exhaustive lists.

## v0.7.8 highlights — 2026-05-06

### Packages

| Package | Version | What's new |
|---------|---------|-----------|
| `nucleusiq` | **0.7.8** | Run-local context stack (workspace, evidence dossier, lexical document corpus), automatic L4.5 activation, phase/evidence gate telemetry, synthesis package, shared tool-result serialization, autonomous Critic/Refiner fixes |
| `nucleusiq-openai` | **0.6.3** | Dependency floor **`nucleusiq>=0.7.8`** (package version unchanged) |
| `nucleusiq-gemini` | **0.2.5** | Dependency floor **`nucleusiq>=0.7.8`** (package version unchanged) |
| `nucleusiq-groq` | **0.1.0a1** | **New** — Groq Chat Completions via official **`groq`** SDK; local tools, streaming, structured output (model-dependent); **`nucleusiq>=0.7.8`** |

### Run-local context state (L4 / analyst notebook)

- **`InMemoryWorkspace`** (`nucleusiq.agents.context.workspace`) — bounded per-run notebook (notes, artifacts, summaries) with `WorkspaceEntry`, `WorkspaceStats`, `WorkspaceLimitError`.
- **Workspace tools** (`nucleusiq.agents.context.workspace_tools`) — `build_workspace_tools`: `write_workspace_note`, `write_workspace_artifact`, `list_workspace_entries`, `read_workspace_entry`, `summarize_workspace`. Helpers **`is_workspace_tool_name`**, **`is_context_management_tool_name`** (all framework-injected context helpers skip the user’s external tool budget).

### Structured evidence (L4)

- **`InMemoryEvidenceDossier`** + **`EvidenceItem`** (`nucleusiq.agents.context.evidence`) — claims with status, confidence, tags, quotes, provenance.
- **Evidence tools** (`nucleusiq.agents.context.evidence_tools`) — **`build_evidence_tools`**: `add_evidence`, `add_evidence_gap`, `list_evidence`, `summarize_evidence`, `evidence_coverage`; **`is_evidence_tool_name`**.

### Lexical document corpus (L5)

- **`InMemoryDocumentCorpus`** (`nucleusiq.agents.context.document_search`) — indexes caller-provided **text** into bounded chunks with lexical search (`DocumentRef`, `DocumentChunk`, `ChunkHit`, `DocumentSearchStats`). No PDF parsing, embeddings, or Task E logic in this surface.
- **Corpus tools** (`nucleusiq.agents.context.document_corpus_tools`) — **`build_document_corpus_tools(corpus, evidence=…)`**: `search_document_corpus`, `get_document_chunk`, `list_indexed_documents`, `promote_document_chunk_to_evidence`; **`is_document_corpus_tool_name`**.

### L4.5 activation

- **`ContextStateActivator`** (`nucleusiq.agents.context.state_activator`) — after each **business** tool result (skips framework context tools): strict promotion into evidence when shaped like facts; **light ingest** into workspace + corpus with guards (tool-name hints, length gates, false-positive filters).
- **`ContextActivationMetrics`** — counters surfaced as **`AgentResult.metadata["context_activation"]`**.

### L6 phase control & evidence gate

- **`PhaseController`** + **`AgentPhase`** (`nucleusiq.agents.context.phase_control`) — ordered phases, durations, evidence-gate outcomes, flags (`synthesis_used_package`, `critic_used_package`, `refiner_used_gaps`). **`PhaseStats.to_dict()`** → **`AgentResult.metadata["phase_control"]`**.
- **`EvidenceGate`** + **`EvidenceGateDecision`** — optional tag-based completeness vs the dossier.
- **`AgentConfig`** — **`evidence_gate_required_tags`**, **`evidence_gate_enforce`**, **`context_tool_result_corpus_max_chars`** (per-result corpus cap; `0` disables), **`context_activation_ingest_min_chars`** (minimum text size for light ingest when not evidence-shaped).

### Synthesis package

- **`SynthesisPackage`** + **`build_synthesis_package`** (`nucleusiq.agents.context.synthesis_package`) — bounded final input from workspace + evidence + recalled snippets. **`Agent.build_synthesis_package`** / **`_last_synthesis_package`**; **`AgentResult.metadata["synthesis_package"]`** when present.

### Agent wiring & metadata

- **`Agent`** lazy accessors: **`workspace`**, **`evidence_dossier`**, **`document_corpus`**, **`phase_controller`**, **`evidence_gate`**, **`build_synthesis_package`**.
- **`AgentResult.metadata`** may include **`workspace`**, **`evidence`**, **`document_search`**, **`phase_control`**, **`context_activation`**, **`synthesis_package`** (alongside **`context_telemetry`** on the result).

### Serialization & autonomous behavior

- **`tool_result_to_context_string`** (`nucleusiq.agents.modes.tool_payload`) — shared by base/standard/direct modes; **`str`** tool results are **not** double JSON-encoded.
- **`CriticRunner`** — any critique exception → **`Verdict.UNCERTAIN`**, score **`0.0`**, explicit feedback (safer than treating failures as pass).
- **`SimpleRunner`** — after Refiner success, **`_last_messages`** refreshed so the next Critic sees the revised trace.

### Validation

Upstream gate (see [CHANGELOG.md](https://github.com/nucleusbox/NucleusIQ/blob/main/CHANGELOG.md#078)): **2554 passed**, **2 skipped** with `pytest tests --ignore=tests/memory/integration` (~2026-05-06).

### Documentation

- **[Groq provider](../python/nucleusiq/guides/groq-provider.md)** — Install, env vars, **`BaseGroq`** / **`GroqLLMParams`**, Phase A limitations, links to monorepo examples.
- **[Context stack layers (L0–L7)](../python/nucleusiq/context-stack-layers.md)** — unified map from compaction tiers (**L0–L3**) through run-local state (**L4–L6**) to synthesis/`AgentResult` (**L7**).
- **[Run-local context state](../python/nucleusiq/run-local-context-state.md)** — deep dive on **L4–L6**, tools, config, **`AgentResult.metadata`**.

See the full [CHANGELOG.md on GitHub](https://github.com/nucleusbox/NucleusIQ/blob/main/CHANGELOG.md#078--2026-05-06) for the authoritative list and CI notes.

## v0.7.7 highlights

### Packages

| Package | Version | What's new |
|---------|---------|-----------|
| `nucleusiq` | **0.7.7** | Stable Context Management v2 (single `Compactor`, bounded markers, recall/rehydration), idempotent tool metadata, clearer `AgentResult` on errors and tool-cap exhaustion |
| `nucleusiq-openai` | **0.6.3** | Sync with v0.7.7 core message/tool contracts (`nucleusiq>=0.7.7`) |
| `nucleusiq-gemini` | **0.2.5** | Sync with v0.7.7 core message/tool contracts (`nucleusiq>=0.7.7`) |

### Context Management v2

- One compaction pipeline, bounded observation markers, recallable offload, synthesis-time rehydration.
- Default `ContextConfig.squeeze_threshold=0.70` kept after validation on PDF-heavy runs.
- **Fixed:** rehydration uses the engine’s resolved model context window when `max_context_tokens` is auto-detected (was skipping when the field was `None`).

### Tools

- **Opt-in idempotent tools:** `BaseTool.idempotent` and `@tool(idempotent=True)`. Default remains `False` so live-data tools are never deduplicated unless you declare them safe. Identical `(tool_name, args)` short-circuits to the prior result.

### Agent execution & results

- **Mode default tool budgets** when `max_tool_calls` is unset: **Direct 25**, **Standard 80**, **Autonomous 300** tool invocations per run (and the same ceiling applies to how many user tools you register, excluding recall tools). Older docs listed **5 / 30 / 100**; behavior matches `AgentConfig.get_effective_max_tool_calls()` in the framework.
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
- For current test counts and gates, see the [upstream CHANGELOG](https://github.com/nucleusbox/NucleusIQ/blob/main/CHANGELOG.md) for the release you are on (example upstream gate cited for **v0.7.8**: ~2,554 passed with skips per environment).

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
