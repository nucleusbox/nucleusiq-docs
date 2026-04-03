# Changelog

All notable changes to NucleusIQ are documented in the [CHANGELOG.md](https://github.com/nucleusbox/NucleusIQ/blob/main/CHANGELOG.md) in the repository root.

## Recent releases

- **[0.7.4](https://github.com/nucleusbox/NucleusIQ/blob/main/CHANGELOG.md#074)** — ExecutionTracer, Pyrefly type checking, error package restructure, usage extraction, exhaustive error wiring
- **[0.7.3](https://github.com/nucleusbox/NucleusIQ/blob/main/CHANGELOG.md#073)** — Gemini tool-calling fixes, `$ref`/`$defs` inlining for structured output
- **[0.7.2](https://github.com/nucleusbox/NucleusIQ/blob/main/CHANGELOG.md#072)** — Unified exception hierarchy (10 families), AgentResult response contract
- **[0.6.0](https://github.com/nucleusbox/NucleusIQ/blob/main/CHANGELOG.md#060--2026-03-13)** — Gemini provider, `@tool` decorator, cost estimation, framework error taxonomy
- **[0.5.0](https://github.com/nucleusbox/NucleusIQ/blob/main/CHANGELOG.md#050--2026-03-11)** — Token origin split, UsageSummary schema, FileWriteTool, FileExtractTool query filtering

## v0.7.4 highlights

### Packages

| Package | Version | What's new |
|---------|---------|-----------|
| `nucleusiq` | 0.7.4 | ExecutionTracer, Pyrefly CI, error package restructure, usage extraction, exhaustive error wiring |
| `nucleusiq-openai` | 0.6.1 | Compatible with new exception hierarchy and AgentResult contract |
| `nucleusiq-gemini` | 0.2.2 | Tool-calling fixes, `$ref`/`$defs` inlining for structured output |

### Key features

- **ExecutionTracer observability** — full LLM/tool call tracing with `AgentConfig(enable_tracing=True)`, populates `AgentResult.tool_calls`, `.llm_calls`, `.warnings`
- **AgentResult response contract** — typed, immutable Pydantic model returned from `agent.execute()` (v0.7.2)
- **Full exception hierarchy** — 10 error families: Tool, Agent, Attachment, Memory, Prompt, Streaming, Plugin, StructuredOutput, LLM, Workspace (v0.7.2)
- **Gemini tool-calling fixes** — empty `function_response.name`, non-dict response wrapping, `$ref`/`$defs` inlining (v0.7.3)
- **Pyrefly type checking** — 121 type errors fixed, CI-gated static analysis
- **Architecture cleanup** — `core/errors/` package with lazy re-exports, `core/agents/usage/` package for cost and usage tracking

For the full history, see [CHANGELOG.md](https://github.com/nucleusbox/NucleusIQ/blob/main/CHANGELOG.md) on GitHub.
