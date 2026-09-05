# Changelog

All notable changes to NucleusIQ are documented in the [CHANGELOG.md](https://github.com/nucleusbox/NucleusIQ/blob/main/CHANGELOG.md) in the repository root.

## v0.7.13 — OpenAI-compatible provider (2026-09-05)

!!! success "Self-hosted and bring-your-own-model"

    One new package for every Chat Completions server. See the dedicated [v0.7.13 release notes](release-notes/v0.7.13.md).

### Packages

| Package | Version | What's new |
|---------|---------|-----------|
| `nucleusiq` | **0.7.13** | `BaseLLM.PROVIDER_NAME` — provider identity is declared, not guessed from the class name. Dead `supports_native_output()` removed. `OutputMode.AUTO` still resolves to NATIVE (hand the schema to the adapter). |
| `nucleusiq-openai-compatible` | **0.1.0** | 🟢 **New, Stable.** BYOM / BYOK for vLLM, SGLang, TGI, llama.cpp, LM Studio, NIM, Ollama `/v1`, Azure OpenAI v1, OpenRouter, Together, and other Chat Completions servers. Engine presets, auth strategies, `validate()`, structured-output policies. **675 tests, 99.40% coverage.** Requires `nucleusiq>=0.7.13`. |
| `nucleusiq-openai` | **0.7.1** | Responses API usage: `input_tokens` / `output_tokens` → `prompt_tokens` / `completion_tokens`. Non-streaming `call()` no longer reports 0 tokens / $0.00. |
| `nucleusiq-mcp` | **0.1.1** | Security floor `mcp>=1.28.1` (session auth, task isolation, WebSocket Host/Origin). |
| `nucleusiq-gemini` | **0.3.1** | Declares `PROVIDER_NAME` and `pydantic`. README examples use valid `Agent(prompt=...)`. |
| `nucleusiq-anthropic` | **0.2.1** | Declares `PROVIDER_NAME` plus `httpx` / `pydantic`. |
| `nucleusiq-ollama` | **0.2.1** | same |
| `nucleusiq-groq` | **0.1.1** | same |

Only the new provider floors on `nucleusiq>=0.7.13`. **4,382 tests** passing across the monorepo.

### Highlights

- 🖥️ Point any existing `Agent` at **your** vLLM / SGLang / llama.cpp / LM Studio server.
- 🔑 Bring-your-own-key: `NoAuth`, `BearerAuth`, `HeaderAuth`, or a callable resolved once per request.
- 🧭 `await llm.validate()` checks reachability, auth, and served model names before an agent run.
- 🔒 All 32 Dependabot advisories cleared. `mcp>=1.28.1` is the only advisory that reached published metadata.

### Documentation

- **[v0.7.13 release notes](release-notes/v0.7.13.md)**
- **[OpenAI-compatible provider](../python/nucleusiq/guides/openai-compatible-provider.md)**
- **[OpenAI-compatible quickstart](../python/nucleusiq/examples/openai-compatible-quickstart.md)**
- Monorepo [CHANGELOG.md — 0.7.13](https://github.com/nucleusbox/NucleusIQ/blob/main/CHANGELOG.md#0713--2026-09-05)

## v0.7.12 — coordinated stable release (2026-05-26)

!!! success "Every alpha/beta provider promoted to Stable in one release"

    The largest release since the project began. See the dedicated [v0.7.12 release notes](release-notes/v0.7.12.md) for the full deep-dive.

### Packages

| Package | Version | What's new |
|---------|---------|-----------|
| `nucleusiq` | **0.7.12** | Central `provider` detection + `ToolCallRecord.executed_by="local"\|"provider"`; `LLMCallRecord` gains `provider`, `request_id`, `organization_id`, `stop_reason`, `cache_read_input_tokens`, `cache_creation_input_tokens`, `metadata`; new `build_server_tool_call_records` observability helper |
| `nucleusiq-anthropic` | **0.2.0** | 🟢 **Stable** — Phase B complete: `AnthropicTool.web_search()` / `web_fetch()` / `code_execution()`, prompt caching (`cache_system` / `cache_tools`), extended thinking (`thinking="low"\|"medium"\|"high"\|"max"`), `strict_tools`, `disable_parallel_tool_use`; server-tool observability via `server_tool_use` + per-tool `*_tool_result` parsing; **151 unit + 6 live integration tests, 95.91% coverage** |
| `nucleusiq-ollama` | **0.2.0** | 🟢 **Stable** — vision wire: OpenAI-style multimodal `content` lists split into Ollama's `content` + `images`, `data:` URL decoding, HTTP-URL warning; provider tag on `LLMCallRecord`; **98 unit tests, 99.85% coverage** |
| `nucleusiq-groq` | **0.1.0** | 🟢 **Stable** — `message.executed_tools` parsed into `GroqLLMResponse.server_tool_calls`; provider tag; **79 unit tests, 92.51% coverage** |
| `nucleusiq-mcp` | **0.1.0** | 🟢 **Stable** — promoted from beta (same Phase 0–3 surface); **235 unit + 13 live integration tests, 98.68% coverage** |
| `nucleusiq-openai` | **0.7.0** | 🟢 Stable — native-tool observability via `ServerToolCall` (`web_search_call`, `code_interpreter_call`, `file_search_call`, `computer_use_call`, `image_generation_call`); **232 unit tests** |
| `nucleusiq-gemini` | **0.3.0** | 🟢 Stable — native-tool observability (`executable_code` + `code_execution_result` → `code_execution`; `grounding_metadata` → `google_search`); **292 unit tests** |

All providers floor on `nucleusiq>=0.7.12`. After v0.7.12 the project returns to a **bug-fix / single-provider cadence**.

### Highlights

- 🧠 Anthropic Phase B with **6 live integration tests** against the real API.
- 🔎 Provider-agnostic `executed_by` field on every `ToolCallRecord` — split local vs provider execution with a single query, across **every** provider.
- 👁️ Ollama vision messages now Just Work — paste OpenAI-style multimodal `content` lists and `nucleusiq-ollama` converts them to the right wire shape.
- 📊 Six new fields on `LLMCallRecord` for cost analysis (`cache_read_input_tokens`, `cache_creation_input_tokens`) and cross-system correlation (`provider`, `request_id`, `organization_id`, `stop_reason`).
- ✅ **3 705+ tests passing across the monorepo.**

### Documentation

- **[v0.7.12 release notes](release-notes/v0.7.12.md)** — the deep-dive page
- **[Anthropic provider](../python/nucleusiq/guides/anthropic-provider.md)** — full Phase B reference
- **[Native server tools](../python/nucleusiq/guides/native-server-tools.md)** — cross-cutting concept
- **[Prompt caching](../python/nucleusiq/guides/prompt-caching.md)**
- **[Extended thinking](../python/nucleusiq/guides/extended-thinking.md)**
- **[Observability — native-tool observability (v0.7.12)](../python/nucleusiq/observability/index.md#native-tool-observability-v0712)** — new `executed_by` + `LLMCallRecord` fields
- **[Ollama provider](../python/nucleusiq/guides/ollama-provider.md)** — vision wire
- **[MCP integration](../python/nucleusiq/guides/mcp-integration.md)** — 0.1.0 Stable

## v0.7.11 + MCP tool adapter (now Stable in v0.7.12)

### Packages

| Package | Version | What's new |
|---------|---------|-----------|
| `nucleusiq` | **0.7.11** | **`ExpandableTool`** protocol — any tool factory (like **`MCPTool`**) can expand into many **`BaseTool`** instances during **`Agent.initialize()`** without the core knowing about specifics; parallel-safe **`Agent.initialize()`** with **`asyncio.gather(return_exceptions=True)`** and **`BaseException`**-safe cleanup; **`ToolCallRecord.source`** plumbed end-to-end from tool → tracer for **`mcp://`** origin tagging; optional **`nucleusiq[mcp]`** extras |
| `nucleusiq-mcp` | **0.1.0b1** | **New beta** — universal **[Model Context Protocol](https://modelcontextprotocol.io/)** adapter on the official **`mcp`** SDK; supports **stdio + Streamable HTTP + SSE** transports (auto-detected); auth strategies **`BearerAuth`**, **`OAuthAuth`** (OAuth 2.1 + PKCE), **`EnvAuth`**, **`CustomHeadersAuth`** with shorthand **`auth="..."`**; **`on_connect_failure="raise"|"skip"`** + **`health_check=True`** + **`MCPTool.ping()`**; decorator filters **`@mcp_tool_filter`**; per-server source attribution on every tool call; **235** unit tests (**98.68%** coverage) + **13** live integration tests across all three transports; requires **`nucleusiq>=0.7.11`**, **`mcp>=1.27,<2`** |

### Highlights

- **One `MCPTool` line per server** — transport auto-detected, auth typed or shorthand, env vars forwarded for stdio.
- **Works with every LLM provider** — OpenAI, Anthropic, Gemini, Groq, Ollama, Mock.
- **Source attribution** — every `ToolCallRecord` produced by an MCP tool carries **`source="mcp://server=<name> (path=A)"`** for observability.
- **Resilient initialization** — multiple MCP servers connect in parallel; one bad peer no longer leaks tasks or skips cleanup.
- **Plugin guardrails apply** — **`ToolGuardPlugin`**, **`HumanApprovalPlugin`**, **`ToolCallLimitPlugin`** all work on MCP tools because they are normal **`BaseTool`** instances.

### Documentation

- **[MCP integration guide](../python/nucleusiq/guides/mcp-integration.md)** — Beta announcement, transports, auth strategies, filtering, OAuth, observability, comparison vs OpenAI server-side MCP.
- **[MCP quickstart](../python/nucleusiq/examples/mcp-quickstart.md)** — Seven copy-paste patterns: stdio, HTTP + Bearer, multi-server, filter/rename, graceful degradation, source tracing, plugin guardrails.

Runnable scripts: **`src/providers/tools/mcp/examples/`** (`01_basic_stdio.py` … `08_full_agent_with_llm.py`). Notebook demo: **`notebooks/agents/mcp_tools_showcase.ipynb`** (Windows-friendly Streamable HTTP path).

## Preview — Anthropic Claude (**alpha**)

Shipped under **[Unreleased](https://github.com/nucleusbox/NucleusIQ/blob/main/CHANGELOG.md)** until the next tagged core release:

- **`nucleusiq-anthropic` 0.1.0a1** — **`BaseAnthropic`**, **`AnthropicLLMParams`** (**`top_k`**, beta headers, **`extra_headers`**), Messages API wiring, **`@tool`** loops, streaming (**`StreamEvent`**), native **JSON Schema** structured outputs (**`output_config.format`**) when the model supports them; SDK errors → **`nucleusiq.llms.errors`** with **`retry_policy`** (**`Retry-After`** aware). Requires **`nucleusiq>=0.7.10`**, **`anthropic>=0.40,<1`**. **100+** unit tests in CI.

### Documentation

- **[Anthropic provider](../python/nucleusiq/guides/anthropic-provider.md)** — Alpha announcement, capability matrix, env, structured-output caveats.
- **[Anthropic quickstart](../python/nucleusiq/examples/anthropic-quickstart.md)** — DIRECT / STANDARD / AUTONOMOUS snippets.

Runnable scripts: **`src/providers/llms/anthropic/examples/agents/`** (`01`–`09`) plus **`output_parsers/anthropic_native_structured_example.py`**.

## Recent releases

- **[0.7.11 + MCP beta](https://github.com/nucleusbox/NucleusIQ/blob/main/CHANGELOG.md)** — **`nucleusiq` 0.7.11** (`ExpandableTool` protocol, parallel-safe init, `ToolCallRecord.source`) + **`nucleusiq-mcp` 0.1.0b1** beta (universal MCP adapter, stdio + HTTP + SSE, OAuth/Bearer/Env/Custom auth)
- **[Unreleased / Anthropic alpha](https://github.com/nucleusbox/NucleusIQ/blob/main/CHANGELOG.md#unreleased)** — **`nucleusiq-anthropic` 0.1.0a1** (**Messages API**, official **`anthropic`** SDK)
- **[0.7.10](https://github.com/nucleusbox/NucleusIQ/blob/main/CHANGELOG.md#0710)** — **`nucleusiq[http]`** optional extra + **`urllib3`** lock hygiene; structured-output resolver (**Ollama** / Groq); **`nucleusiq-ollama` 0.1.0a1** (**alpha**, **`nucleusiq>=0.7.10`**)
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

## v0.7.10 highlights — 2026-05-09

### Packages

| Package | Version | What's new |
|---------|---------|-----------|
| `nucleusiq` | **0.7.10** | Security-focused dependency graph (**`urllib3`**); optional **`nucleusiq[http]`**; **`structured_output.resolver`** recognizes **`ollama`** / **`groq`** LLMs for **`OutputSchema`** |
| `nucleusiq-ollama` | **0.1.0a1** | **New alpha** — **`BaseOllama`**, **`OllamaLLMParams`** (**`think`**, **`keep_alive`**), tools, streaming, structured **`format`**; **`nucleusiq>=0.7.10`**, **`ollama>=0.5,<1`** |

### Ollama provider (alpha)

- Official **`ollama`** Python SDK (**no LangChain**); **`OLLAMA_HOST`** / **`OLLAMA_API_KEY`** / **`OLLAMA_MODEL`** env passthrough patterns match monorepo examples.
- Runnable matrix: **`src/providers/inference/ollama/examples/agents/`** (`00`–`03`).

### Documentation

- **[Ollama provider](../python/nucleusiq/guides/ollama-provider.md)** — Alpha scope, env, capabilities, limitations.
- **[Ollama quickstart](../python/nucleusiq/examples/ollama-quickstart.md)** — DIRECT / STANDARD snippets.

See the full [CHANGELOG.md on GitHub](https://github.com/nucleusbox/NucleusIQ/blob/main/CHANGELOG.md#0710--2026-05-09) for security notes and exhaustive lists.

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
