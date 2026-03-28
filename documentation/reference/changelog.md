# Changelog

All notable changes to NucleusIQ are documented in the [CHANGELOG.md](https://github.com/nucleusbox/NucleusIQ/blob/main/CHANGELOG.md) in the repository root.

## Recent releases

- **[0.6.0](https://github.com/nucleusbox/NucleusIQ/blob/main/CHANGELOG.md#060--2026-03-13)** — Gemini provider, `@tool` decorator, cost estimation, framework error taxonomy, LLM parameter standardization (2,285 tests)
- **[0.5.0](https://github.com/nucleusbox/NucleusIQ/blob/main/CHANGELOG.md#050--2026-03-11)** — Token origin split, UsageSummary schema, FileWriteTool, FileExtractTool query filtering
- **[0.4.0](https://github.com/nucleusbox/NucleusIQ/blob/main/CHANGELOG.md#040--2026-03-10)** — Multimodal attachments, 4 built-in file tools, UsageTracker, AttachmentGuardPlugin
- **[0.3.0](https://github.com/nucleusbox/NucleusIQ/blob/main/CHANGELOG.md#030--2026-02-27)** — End-to-end streaming, StreamEvent model

## v0.6.0 highlights

### New packages

| Package | Version | What's new |
|---------|---------|-----------|
| `nucleusiq` | 0.6.0 | Error taxonomy, `@tool` decorator, cost tracker, `max_output_tokens` standardization |
| `nucleusiq-openai` | 0.5.0 | Framework error mapping, parameter standardization |
| `nucleusiq-gemini` | 0.1.0 | **New** — Google Gemini provider with streaming, native tools, structured output |

### Key features

- **Google Gemini provider** — full `BaseLLM` implementation with Google Search, Code Execution, URL Context, Google Maps native tools
- **`@tool` decorator** — create tools from plain functions, auto-generates JSON schema from type hints
- **Cost estimation** — `CostTracker` with built-in pricing for 15 OpenAI/Gemini models
- **Framework error taxonomy** — provider-agnostic exception hierarchy (`RateLimitError`, `AuthenticationError`, etc.)
- **LLM parameter standardization** — universal `max_output_tokens` across all providers

For the full history, see [CHANGELOG.md](https://github.com/nucleusbox/NucleusIQ/blob/main/CHANGELOG.md) on GitHub.
