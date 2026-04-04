# Changelog

All notable changes to NucleusIQ are documented in the [CHANGELOG.md](https://github.com/nucleusbox/NucleusIQ/blob/main/CHANGELOG.md) in the repository root.

## Recent releases

- **[0.7.5](https://github.com/nucleusbox/NucleusIQ/blob/main/CHANGELOG.md#075)** — Gemini native + custom tool mixing (proxy pattern), full observability wiring
- **[0.7.4](https://github.com/nucleusbox/NucleusIQ/blob/main/CHANGELOG.md#074)** — ExecutionTracer, Pyrefly type checking, error package restructure, usage extraction, exhaustive error wiring
- **[0.7.3](https://github.com/nucleusbox/NucleusIQ/blob/main/CHANGELOG.md#073)** — Gemini tool-calling fixes, `$ref`/`$defs` inlining for structured output
- **[0.7.2](https://github.com/nucleusbox/NucleusIQ/blob/main/CHANGELOG.md#072)** — Unified exception hierarchy (10 families), AgentResult response contract
- **[0.6.0](https://github.com/nucleusbox/NucleusIQ/blob/main/CHANGELOG.md#060--2026-03-13)** — Gemini provider, `@tool` decorator, cost estimation, framework error taxonomy
- **[0.5.0](https://github.com/nucleusbox/NucleusIQ/blob/main/CHANGELOG.md#050--2026-03-11)** — Token origin split, UsageSummary schema, FileWriteTool, FileExtractTool query filtering

## v0.7.5 highlights

### Packages

| Package | Version | What's new |
|---------|---------|-----------|
| `nucleusiq` | 0.7.5 | Full observability wiring — PluginEvent, MemorySnapshot, AutonomousDetail tracing |
| `nucleusiq-openai` | 0.6.1 | No changes |
| `nucleusiq-gemini` | 0.2.3 | Native + custom tool mixing via transparent proxy pattern |

### Part A: Gemini Native + Custom Tool Mixing

Google's Gemini 2.5 API rejects requests that mix native tools (`google_search`, `code_execution`, `url_context`, `google_maps`) with custom function declarations. NucleusIQ v0.7.5 resolves this transparently with a **proxy pattern** — entirely within the Gemini provider, zero core framework changes.

- **`tool_splitter.py`** — detects mixed tools, classifies native vs custom, builds proxy specs
- **`_GeminiNativeTool` proxy mode** — native tools masquerade as function declarations; `execute()` makes a real `generateContent` sub-call with the native tool
- **`BaseGemini.convert_tool_specs()`** — auto-enables proxy when mixed, reverts when not
- Works across **all execution modes** (Direct, Standard, Autonomous) and all Gemini models
- No other framework provides a transparent solution: LangChain blocks it, ADK requires sub-agents, CrewAI/AutoGen don't address it

See [Gemini provider guide — Mixing native and custom tools](../python/nucleusiq/guides/gemini-provider.md#mixing-native-and-custom-tools).

### Part B: Full Observability Wiring

`AgentResult` now captures every dimension of an execution when `enable_tracing=True`:

| New field | What it captures |
|-----------|-----------------|
| `result.plugin_events` | Every plugin hook fired — name, duration, payload |
| `result.memory_snapshot` | Conversation messages and token count at execution end |
| `result.autonomous` | Decomposition steps, sub-task names, validation records, critic scores |
| `result.llm_calls[].prompt_technique` | Which prompt strategy was used (e.g. `chain_of_thought`) |

Previously invisible operations — `Decomposer.analyze()` LLM calls, plugin hook durations, memory state — are now fully traced.

See [Observability docs](../python/nucleusiq/observability/index.md).

## v0.7.4 highlights

### Key features

- **ExecutionTracer observability** — full LLM/tool call tracing with `AgentConfig(enable_tracing=True)`, populates `AgentResult.tool_calls`, `.llm_calls`, `.warnings`
- **AgentResult response contract** — typed, immutable Pydantic model returned from `agent.execute()` (v0.7.2)
- **Full exception hierarchy** — 10 error families: Tool, Agent, Attachment, Memory, Prompt, Streaming, Plugin, StructuredOutput, LLM, Workspace (v0.7.2)
- **Gemini tool-calling fixes** — empty `function_response.name`, non-dict response wrapping, `$ref`/`$defs` inlining (v0.7.3)
- **Pyrefly type checking** — 121 type errors fixed, CI-gated static analysis
- **Architecture cleanup** — `core/errors/` package with lazy re-exports, `core/agents/usage/` package for cost and usage tracking

For the full history, see [CHANGELOG.md](https://github.com/nucleusbox/NucleusIQ/blob/main/CHANGELOG.md) on GitHub.
